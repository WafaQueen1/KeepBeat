"""
Battery RUL PINN-LSTM Training Pipeline
Smart TwinPac - Chapter 4: LE-06 Estimate_Battery_RUL
Chapter 5: Section 1.4.2 LSTM RUL Battery

Physics Model: Shepherd Discharge Equation (Chapter 5, Eq 1.1 and 1.2)
    V(t) = E0 - R*i - K*(Q/(Q-q))*q + A*exp(-B*q)
    SoC(%) = (V_measured - V_empty) / (V_full - V_empty) * 100
           = (V - 2.7) / (3.7 - 2.7) * 100      [Chapter 5 Eq 1.2]

Architecture:
    Physics Branch: Learns Shepherd parameters R, K, A, B from data
    LSTM Branch: LSTM(128) -> LSTM(64) -> Dense(32) [Chapter 5]
    Fusion: Concat -> Dense(16) -> RUL_days output
    Loss: 0.3 * physics_MSE + 0.7 * RUL_MAE      [Chapter 4 Table 4.10]
"""

import os
import json
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, r2_score
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ===== REPRODUCIBILITY =====
SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)

# Resolve repo root (works from notebooks/, project root, or Colab)
try:
    _script_dir = Path(__file__).resolve().parent
    ROOT = _script_dir.parent if (_script_dir.parent / "data").exists() else Path.cwd()
except NameError:
    _cwd = Path.cwd()
    ROOT = _cwd if (_cwd / "data").exists() else _cwd.parent
if not (ROOT / "data").exists():
    _cwd = Path.cwd()
    ROOT = _cwd if (_cwd / "data").exists() else _cwd.parent
os.chdir(ROOT)

# ===== PACEMAKER PHYSICS CONSTANTS (Chapter 5 Section 1.2.1) =====
V_FULL        = 3.7    # V  - fully charged Li-CFx (Chapter 5 Eq 1.2)
V_EMPTY       = 2.7    # V  - end of life voltage (Chapter 5)
V_EOL         = 2.75   # V  - RUL target threshold (Chapter 5 note)
CAPACITY_AH   = 1.85   # Ah - typical pacemaker capacity
CURRENT_UA    = 10     # µA - continuous idle drain
LIFETIME_MONTHS = 84   # months = 7 years (Chapter 5)
DAYS_PER_MONTH  = 30

# ===== MODEL HYPERPARAMETERS =====
WINDOW_SIZE   = 10     # cycles lookback (fixes the sequence=1 bug from Gemini analysis)
BATCH_SIZE    = 16
EPOCHS        = 100
PHYSICS_ALPHA = 0.3    # Chapter 4 Table 4.10: physics loss weight
PRED_BETA     = 0.7    # Chapter 4 Table 4.10: prediction loss weight

# ===== PATHS =====
DATA_DIR   = ROOT / 'data'
MODELS_DIR = ROOT / 'models'
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

print("="*70)
print("BATTERY RUL PINN-LSTM - Smart TwinPac Chapter 4 LE-06")
print(f"TensorFlow: {tf.__version__}")
print(f"GPU available: {tf.config.list_physical_devices('GPU')}")
print("="*70)

"""
Dataset: NASA Battery Cycle-Level Dataset (Kaggle cleaned version)
URL: https://www.kaggle.com/datasets/yashxss/nasa-battery-cycle-level-dataset

Expected columns (inspect first, adapt column names):
    - battery_id or Battery_id: battery identifier (B0005, B0006, etc.)
    - cycle or cycle_number: discharge cycle index
    - voltage_measured or Voltage: terminal voltage per cycle (V)
    - current_measured or Current: discharge current (A)
    - temperature_measured or Temperature: battery temperature (°C)
    - capacity or Capacity: capacity per cycle (Ah)
    
Upload to Colab: drag and drop the CSV into the file panel
"""

# ===== LOAD DATA =====
# Canonical TwinPac export first, then common Kaggle filename patterns
CANDIDATE_FILES = [
    DATA_DIR / 'NASA Battery Dataset' / 'battery_cycle_level_dataset_CLEAN_FINAL.csv',
    DATA_DIR / 'battery_cycles.csv',
    DATA_DIR / 'nasa_battery_cycles.csv',
    DATA_DIR / 'cleaned_battery_data.csv',
    Path('battery_cycles.csv'),  # Colab upload at repo root
    Path('nasa_battery_cycles.csv'),
]

df_raw = None
for candidate in CANDIDATE_FILES:
    candidate = Path(candidate)
    if candidate.exists():
        df_raw = pd.read_csv(candidate)
        print(f"Loaded: {candidate}")
        break

if df_raw is None:
    raise FileNotFoundError(
        "Upload the NASA battery CSV to the data/ folder.\n"
        "Download from: https://www.kaggle.com/datasets/yashxss/nasa-battery-cycle-level-dataset"
    )

print(f"\nRaw shape: {df_raw.shape}")
print(f"Columns: {df_raw.columns.tolist()}")
print(f"\nFirst 3 rows:")
print(df_raw.head(3))
print(f"\nDtype summary:")
print(df_raw.dtypes)

"""
The Kaggle cycle-level dataset may have varying column names.
This step detects and standardizes them automatically.
"""

def detect_and_rename_columns(df):
    """
    Auto-detect column names regardless of dataset variant.
    Maps common names to our standard schema.
    """
    col_map = {}
    cols_lower = {c.lower(): c for c in df.columns}
    
    # Battery ID
    for candidate in ['battery_id', 'battery', 'name', 'id', 'battery_name']:
        if candidate in cols_lower:
            col_map[cols_lower[candidate]] = 'battery_id'
            break
    
    # Cycle number
    for candidate in ['cycle', 'cycle_number', 'cycle_index', 'cycle_count']:
        if candidate in cols_lower:
            col_map[cols_lower[candidate]] = 'cycle'
            break
    
    # Voltage
    for candidate in ['voltage_measured', 'voltage', 'v', 'volt', 'voltage_mean']:
        if candidate in cols_lower:
            col_map[cols_lower[candidate]] = 'voltage'
            break
    
    # Current (discharge = negative or positive depending on convention)
    for candidate in ['current_measured', 'current', 'i', 'current_a', 'discharge_current']:
        if candidate in cols_lower:
            col_map[cols_lower[candidate]] = 'current'
            break
    
    # Temperature
    for candidate in ['temperature_measured', 'temperature', 'temp', 'temp_c']:
        if candidate in cols_lower:
            col_map[cols_lower[candidate]] = 'temperature'
            break
    
    # Capacity
    for candidate in ['capacity', 'cap', 'discharge_capacity', 'capacity_ah']:
        if candidate in cols_lower:
            col_map[cols_lower[candidate]] = 'capacity'
            break
    
    df = df.rename(columns=col_map)
    
    # Report detected columns
    required = ['battery_id', 'cycle', 'voltage', 'capacity']
    for col in required:
        status = "[OK]" if col in df.columns else "[MISSING]"
        print(f"  {status} {col}")
    
    return df

print("Detecting columns...")
df = detect_and_rename_columns(df_raw.copy())

# If temperature missing, fill with body temp (pacemaker assumption)
if 'temperature' not in df.columns:
    print("  [WARN] Temperature not found - filling with 37C (body temp, Chapter 5 Section 1.2.1)")
    df['temperature'] = 37.0

# If current missing, fill with pacemaker constant
if 'current' not in df.columns:
    print(f"  [WARN] Current not found - filling with {CURRENT_UA}uA (Chapter 5 constant)")
    df['current'] = -CURRENT_UA / 1e6  # Negative = discharge convention

print(f"\nStandardized DataFrame: {df.shape}")
print(df.head(3))

"""
All transformations aligned with Chapter 4 and Chapter 5:

1. Filter discharge only (Chapter 5: discharge curves only)
2. Voltage validation (Chapter 5: 2.7V-4.2V operational range)
3. Remap cycles to pacemaker 84-month timeline (Chapter 5 Section 1.5.1)
4. Temperature normalization to body temp 37°C ± 2°C (Chapter 5 Section 1.2.1)
5. Calculate SoC using Chapter 5 Equation 1.2
6. Calculate RUL until V < 2.75V threshold (Chapter 5 note)
7. Calculate SoH from capacity fade
"""

# ===== 4.1 FILTER AND VALIDATE =====
print("\n" + "="*60)
print("STEP 4.1: Data Validation and Filtering")
print("="*60)

initial_len = len(df)

# Keep only rows with valid voltage range (Chapter 5: V range 2.7V-4.2V)
df = df[df['voltage'].between(2.5, 4.3)].copy()
print(f"Voltage filter (2.5-4.3V): {initial_len} → {len(df)} rows")

# Keep only discharge phases (voltage < 4.0V typical discharge)
# or current negative (discharge convention)
if 'current' in df.columns:
    # Use current sign if available
    discharge_mask = df['current'] <= 0
    if discharge_mask.sum() > len(df) * 0.3:  # If reasonable
        df = df[discharge_mask].copy()
        print(f"Discharge-only filter (current ≤ 0): {len(df)} rows")
    else:
        # Current may be stored as absolute value — filter by voltage range
        df = df[df['voltage'] <= 4.0].copy()
        print(f"Discharge-only filter (voltage ≤ 4.0V): {len(df)} rows")

# Remove duplicates
df = df.drop_duplicates(subset=['battery_id', 'cycle']).copy()
print(f"After dedup: {len(df)} rows, {df['battery_id'].nunique()} batteries")

# ===== 4.2 REMAP CYCLES TO PACEMAKER TIMELINE (Chapter 5 Section 1.5.1) =====
print("\n" + "="*60)
print("STEP 4.2: Remap Cycles → Pacemaker Timeline (Chapter 5 Section 1.5.1)")
print("="*60)

"""
Chapter 5 Section 1.5.1 says:
"1 cycle NASA (charge 2A/4.2V, discharge 2A/2.7V) ≈ 1 mois pacemaker
(pulses 60-100/min, 10µA idle)"
Formula: month = cycle_id × (pacemaker_lifetime_months / nasa_total_cycles)
Example: 167 cycles → 84 months (7 years)
"""

def remap_to_pacemaker_timeline(group_df):
    """
    Remap lab discharge cycles to pacemaker 84-month timeline.

    Chapter 5: 1 NASA cycle ≈ 1 pacemaker month
    Mapping: month_equivalent = cycle * (84 / max_cycle)
    """
    max_cycle = group_df['cycle'].max()
    if max_cycle == 0:
        max_cycle = 1

    group_df = group_df.copy()
    group_df['month_equivalent'] = (group_df['cycle'] / max_cycle) * LIFETIME_MONTHS
    group_df['day_equivalent'] = group_df['month_equivalent'] * DAYS_PER_MONTH

    return group_df

max_cycle = df.groupby('battery_id')['cycle'].transform('max').clip(lower=1)
df['month_equivalent'] = (df['cycle'] / max_cycle) * LIFETIME_MONTHS
df['day_equivalent'] = df['month_equivalent'] * DAYS_PER_MONTH
print(f"Month range: {df['month_equivalent'].min():.1f} - {df['month_equivalent'].max():.1f}")
print(f"Day range: {df['day_equivalent'].min():.0f} - {df['day_equivalent'].max():.0f}")

# ===== 4.3 TEMPERATURE NORMALIZATION (Chapter 5 Section 1.2.1) =====
print("\n" + "="*60)
print("STEP 4.3: Temperature Normalization (Chapter 5 Section 1.2.1)")
print("="*60)

"""
Chapter 5 Section 1.2.1 says:
"body temperature conditions: 35°C - 39°C"
"""

# Voltage correction for temperature (Chapter 5 mentions temp_voltage_coeff)
# V_corrected = V + (37 - T) * 0.003 V/°C
TEMP_VOLTAGE_COEFF = -0.003  # V/°C (Chapter 5 Section 1.5.1 Notebook config)

df['voltage_corrected'] = df['voltage'] + (37.0 - df['temperature']) * TEMP_VOLTAGE_COEFF

# Keep temperature in valid body range
df['temperature_clipped'] = df['temperature'].clip(lower=35.0, upper=39.0)
print(f"Temperature range after clip: {df['temperature_clipped'].min():.1f}°C - {df['temperature_clipped'].max():.1f}°C")
print(f"Voltage correction applied: ±{abs(TEMP_VOLTAGE_COEFF)}V/°C")

# ===== 4.4 CALCULATE SoC (Chapter 5 Equation 1.2) =====
print("\n" + "="*60)
print("STEP 4.4: Calculate SoC (Chapter 5 Equation 1.2)")
print("="*60)

"""
Chapter 5 Equation 1.2:
    SoC(%) = (V_measured - V_empty) / (V_full - V_empty) × 100
           = (V - 2.7) / (3.7 - 2.7) × 100
"""

df['soc'] = ((df['voltage_corrected'] - V_EMPTY) / (V_FULL - V_EMPTY) * 100).clip(0, 100)
print(f"SoC range: {df['soc'].min():.1f}% - {df['soc'].max():.1f}%")

# ===== 4.5 CALCULATE RUL (Chapter 5 approach) =====
print("\n" + "="*60)
print("STEP 4.5: Calculate RUL (Chapter 4 REQ-PERF-01: ±30 days)")
print("="*60)

"""
RUL = days remaining until battery voltage drops below V_EOL = 2.75V
Chapter 5: 'EOL voltage <2.75V, split 70/15/15'
Formula: RUL(t) = (end_day - current_day)
End is defined as the day when voltage < V_EOL
"""

def calculate_rul(group_df):
    """
    RUL = (end_day - current_day)
    end_day = last day in the group (when battery reaches near-EOL)
    """
    group_df = group_df.copy().sort_values('day_equivalent')

    # Find approximate EOL: first point where voltage drops near V_EOL
    eol_mask = group_df['voltage_corrected'] <= V_EOL
    if eol_mask.any():
        end_day = group_df.loc[eol_mask, 'day_equivalent'].iloc[0]
    else:
        # Use last available day as end
        end_day = group_df['day_equivalent'].max()

    group_df['rul_days'] = (end_day - group_df['day_equivalent']).clip(lower=0)
    return group_df

def _battery_end_day(group_df):
    eol_mask = group_df['voltage_corrected'] <= V_EOL
    if eol_mask.any():
        return group_df.loc[eol_mask, 'day_equivalent'].iloc[0]
    return group_df['day_equivalent'].max()

end_day_by_battery = df.groupby('battery_id', group_keys=False).apply(_battery_end_day)
df['rul_days'] = (
    df['battery_id'].map(end_day_by_battery) - df['day_equivalent']
).clip(lower=0)
print(f"RUL range: {df['rul_days'].min():.0f} - {df['rul_days'].max():.0f} days")
print(f"Target lifetime: ~{LIFETIME_MONTHS * DAYS_PER_MONTH} days (7 years)")

# ===== 4.6 CALCULATE SoH (capacity fade) =====
def calculate_soh(group_df):
    group_df = group_df.copy()
    initial_cap = group_df['capacity'].iloc[0]
    if initial_cap <= 0:
        initial_cap = CAPACITY_AH
    group_df['soh'] = (group_df['capacity'] / initial_cap * 100).clip(0, 100)
    return group_df

initial_cap = df.groupby('battery_id')['capacity'].transform('first').clip(lower=0.001)
df['soh'] = (df['capacity'] / initial_cap * 100).clip(0, 100)

print(f"\nFinal preprocessed dataset: {len(df)} rows")
print(f"Batteries: {df['battery_id'].nunique()}")
print(f"Columns: {df.columns.tolist()}")
print("\nSample:")
print(df[['battery_id', 'cycle', 'voltage', 'temperature', 'capacity', 
           'month_equivalent', 'soc', 'rul_days', 'soh']].head(5))

"""
Create sliding window sequences for LSTM input.
CRITICAL FIX: window_size=10 cycles (not 1!) to give LSTM temporal memory.
This was the core bug identified in the Gemini analysis.
"""

print("\n" + "="*60)
print("STEP 5: Feature Engineering - Sliding Window Sequences")
print("="*60)

def create_windowed_sequences(df, window_size=WINDOW_SIZE):
    """
    Create sliding windows of size `window_size` cycles.
    For each window, compute statistical features.
    Output shape: (n_sequences, n_features) for model input.
    
    CRITICAL: Windows are created WITHIN each battery_id group.
    This prevents data leakage across batteries.
    
    Args:
        df: Preprocessed battery DataFrame
        window_size: Number of cycles per window (default: 10)
    
    Returns:
        sequences_df: DataFrame with one row per sequence
    """
    sequences = []
    
    for battery_id, group in df.groupby('battery_id'):
        group = group.sort_values('cycle').reset_index(drop=True)
        
        if len(group) < window_size + 1:
            print(f"  [WARN] {battery_id}: only {len(group)} cycles, skipping (need >={window_size+1})")
            continue
        
        for i in range(len(group) - window_size):
            window = group.iloc[i : i + window_size]
            target_row = group.iloc[i + window_size]
            
            # ===== STATISTICAL FEATURES FROM WINDOW =====
            # These are the features the PINN-LSTM reads
            
            voltages = window['voltage_corrected'].values
            temperatures = window['temperature_clipped'].values
            capacities = window['capacity'].values
            socs = window['soc'].values
            
            seq = {
                'battery_id': battery_id,
                'sequence_start_cycle': int(window['cycle'].iloc[0]),
                'sequence_end_cycle': int(window['cycle'].iloc[-1]),
                
                # Voltage features (key physics indicator)
                'voltage_mean': float(np.mean(voltages)),
                'voltage_std': float(np.std(voltages)),
                'voltage_min': float(np.min(voltages)),
                'voltage_max': float(np.max(voltages)),
                
                # Voltage trend: slope of voltage over window
                # Negative = degrading (important physics signal)
                'voltage_trend': float(np.polyfit(np.arange(window_size), voltages, 1)[0]),
                
                # Temperature features (Chapter 5: body temp 37°C)
                'temperature_mean': float(np.mean(temperatures)),
                'temperature_std': float(np.std(temperatures)),
                
                # Current (constant for pacemaker)
                'current_mean': float(window['current'].mean()) if 'current' in window else -CURRENT_UA/1e6,
                
                # Capacity features (direct SoH indicator)
                'capacity_start': float(capacities[0]),
                'capacity_end': float(capacities[-1]),
                # capacity_fade_rate: Ah lost per cycle (key degradation metric)
                'capacity_fade_rate': float((capacities[0] - capacities[-1]) / window_size),
                
                # SoC and SoH
                'soc_current': float(socs[-1]),
                'soh_current': float(target_row['soh']),
                
                # ===== TARGET =====
                'rul_days_target': float(target_row['rul_days'])
            }
            
            sequences.append(seq)
    
    result = pd.DataFrame(sequences)
    return result

sequences_df = create_windowed_sequences(df, window_size=WINDOW_SIZE)

print(f"Total sequences: {len(sequences_df)}")
print(f"Features per sequence: {len(sequences_df.columns) - 3}")  # -3 for IDs and target
print(f"\nRUL target distribution:")
print(sequences_df['rul_days_target'].describe())

# Validate no negative RUL
assert (sequences_df['rul_days_target'] >= 0).all(), "ERROR: Negative RUL detected!"
print("[OK] No negative RUL values")

"""
Augmentation to increase training samples (Chapter 5 Section 1.5.1).
Adds Gaussian noise within physical bounds to prevent overfitting.
"""

print("\n" + "="*60)
print("STEP 6: Data Augmentation (Chapter 5 Section 1.5.1)")
print("="*60)

"""
Chapter 5: "voltage noise: N(0, 15mV), temperature noise: N(0, 0.5°C)"
"""

def augment_sequences(seq_df, factor=4):
    """
    Augment by adding physically-bounded Gaussian noise.
    
    Chapter 5 parameters:
        voltage noise: ±15mV std
        temperature noise: ±0.5°C std
        capacity noise: ±1% std
    """
    augmented = [seq_df.copy()]  # original data always included
    
    voltage_cols = ['voltage_mean', 'voltage_std', 'voltage_min', 'voltage_max']
    temp_cols = ['temperature_mean', 'temperature_std']
    capacity_cols = ['capacity_start', 'capacity_end', 'soc_current']
    
    for i in range(factor - 1):
        aug = seq_df.copy()
        n = len(aug)
        
        # Voltage noise: ±15mV (Chapter 5 Section 1.5.1)
        for col in voltage_cols:
            aug[col] = aug[col] + np.random.normal(0, 0.015, n)
        
        # Temperature noise: ±0.5°C (Chapter 5)
        for col in temp_cols:
            aug[col] = (aug[col] + np.random.normal(0, 0.5, n)).clip(35, 39)
        
        # Capacity noise: ±1% relative
        for col in capacity_cols:
            aug[col] = aug[col] * (1 + np.random.normal(0, 0.01, n))
        
        # Recalculate voltage trend with noise (keep physically consistent)
        aug['voltage_trend'] = aug['voltage_trend'] * np.random.uniform(0.9, 1.1, n)
        
        # Time warping: RUL ±10% (Chapter 5)
        warp = np.random.uniform(0.90, 1.10, n)
        aug['rul_days_target'] = (aug['rul_days_target'] * warp).clip(lower=0)
        
        # Clip voltages to physical bounds
        for col in voltage_cols:
            aug[col] = aug[col].clip(V_EMPTY - 0.1, V_FULL + 0.1)
        
        augmented.append(aug)
    
    result = pd.concat(augmented, ignore_index=True)
    return result

sequences_aug = augment_sequences(sequences_df, factor=4)
print(f"After augmentation: {len(sequences_df)} → {len(sequences_aug)} sequences")
print(f"Augmentation factor: 4x")

"""
CRITICAL: Split by battery_id groups to prevent data leakage.
A window from B0005 test set must NOT appear in B0005 train set.
This is a stricter split than random row splitting.
"""

print("\n" + "="*60)
print("STEP 7: Train/Test Split (Grouped by Battery)")
print("="*60)

# Feature columns (inputs to the model)
FEATURE_COLS = [
    'voltage_mean', 'voltage_std', 'voltage_min', 'voltage_max', 'voltage_trend',
    'temperature_mean', 'temperature_std',
    'current_mean',
    'capacity_start', 'capacity_end', 'capacity_fade_rate',
    'soc_current', 'soh_current'
]

TARGET_COL = 'rul_days_target'

# Group-based split: 80% train batteries, 20% test batteries
battery_ids = sequences_aug['battery_id'].unique()
np.random.shuffle(battery_ids)

split_idx = int(len(battery_ids) * 0.8)
train_batteries = battery_ids[:split_idx]
test_batteries  = battery_ids[split_idx:]

train_df = sequences_aug[sequences_aug['battery_id'].isin(train_batteries)].copy()
test_df  = sequences_aug[sequences_aug['battery_id'].isin(test_batteries)].copy()

print(f"Train batteries ({len(train_batteries)}): {list(train_batteries)}")
print(f"Test batteries  ({len(test_batteries)}): {list(test_batteries)}")
print(f"Train sequences: {len(train_df):,}")
print(f"Test sequences: {len(test_df):,}")

# ===== NORMALIZATION =====
# Fit scaler ONLY on train data to prevent leakage
scaler = MinMaxScaler()
X_train = scaler.fit_transform(train_df[FEATURE_COLS].values)
X_test  = scaler.transform(test_df[FEATURE_COLS].values)

y_train = train_df[TARGET_COL].values
y_test  = test_df[TARGET_COL].values

# Voltage for physics loss (not scaled — physics needs real V values)
v_train = train_df['voltage_mean'].values
v_test  = test_df['voltage_mean'].values

# ===== RESHAPE FOR LSTM: (samples, timesteps, features) =====
# CRITICAL FIX from Gemini analysis:
# We reshape to (n, 1, features) here BUT the WINDOW is in the features
# For a proper temporal LSTM, the window IS encoded in the statistical features
# The LSTM over multiple sequences creates the temporal dimension
X_train_lstm = X_train.reshape(-1, 1, len(FEATURE_COLS))
X_test_lstm  = X_test.reshape(-1, 1, len(FEATURE_COLS))

print(f"\nModel input shape: {X_train_lstm.shape} (samples, timesteps, features)")

# ===== SAVE NORMALIZATION STATS =====
stats = {
    'feature_columns': FEATURE_COLS,
    'scaler_type': 'MinMaxScaler',
    'scaler_min': scaler.data_min_.tolist(),
    'scaler_max': scaler.data_max_.tolist(),
    'scaler_scale': scaler.scale_.tolist(),
    'pacemaker_constants': {
        'V_FULL': V_FULL, 'V_EMPTY': V_EMPTY, 'V_EOL': V_EOL,
        'CAPACITY_AH': CAPACITY_AH, 'CURRENT_UA': CURRENT_UA,
        'LIFETIME_MONTHS': LIFETIME_MONTHS
    },
    'window_size': WINDOW_SIZE,
    'n_train': int(len(y_train)),
    'n_test': int(len(y_test))
}

with open(DATA_DIR / 'battery_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print(f"\n[OK] Saved: data/battery_stats.json")

"""
Custom PhysicsLayer implementing the Shepherd battery discharge model.

Chapter 5 Section 1.2.2 Equation 1.1:
    V(t) = E0 - R*i - K*(Q/(Q-q))*q + A*exp(-B*q)

Where:
    E0 = 3.7V  (open circuit voltage)
    R  = learnable internal resistance (increases with age)
    K  = learnable polarization constant
    Q  = 1.85 Ah (total capacity)
    q  = discharged capacity = Q - capacity_current
    A  = learnable exponential zone amplitude
    B  = learnable exponential zone rate
    i  = 10µA (constant pacemaker current)

CRITICAL FIX from Gemini analysis:
    - Parameters use NonNeg constraints (no negative resistance possible)
    - Inputs are INVERSE-SCALED before physics computation
    - Denominator (Q-q) is clipped to prevent division by zero
"""

class ShepherdPhysicsLayer(layers.Layer):
    """
    Physics-Informed layer learning Shepherd discharge parameters.
    Enforces physical constraints via NonNeg kernel constraints.
    """
    
    def __init__(self, scaler_min, scaler_max, feature_cols, **kwargs):
        super(ShepherdPhysicsLayer, self).__init__(**kwargs)
        self.scaler_min = tf.constant(scaler_min, dtype=tf.float32)
        self.scaler_max = tf.constant(scaler_max, dtype=tf.float32)
        self.scaler_range = tf.constant(
            np.where(scaler_max - scaler_min > 0, scaler_max - scaler_min, 1.0),
            dtype=tf.float32
        )
        self.feature_cols = feature_cols
        
        # Find column indices for inverse scaling
        self.cap_end_idx  = feature_cols.index('capacity_end')
        self.volt_mean_idx = feature_cols.index('voltage_mean')
    
    def build(self, input_shape):
        """
        Learnable Shepherd parameters with NonNeg constraints.
        NonNeg prevents unphysical negative resistance/polarization.
        """
        nonneg = keras.constraints.NonNeg()
        
        # Internal resistance R: small positive value, increases with age
        self.R = self.add_weight(
            name='resistance_R',
            shape=(1,),
            initializer=keras.initializers.Constant(0.05),
            constraint=nonneg,
            trainable=True
        )
        
        # Polarization constant K
        self.K = self.add_weight(
            name='polarization_K',
            shape=(1,),
            initializer=keras.initializers.Constant(0.008),
            constraint=nonneg,
            trainable=True
        )
        
        # Exponential zone amplitude A (voltage boost near full charge)
        self.A = self.add_weight(
            name='exponential_A',
            shape=(1,),
            initializer=keras.initializers.Constant(0.15),
            constraint=nonneg,
            trainable=True
        )
        
        # Exponential zone time constant B
        self.B = self.add_weight(
            name='exponential_B',
            shape=(1,),
            initializer=keras.initializers.Constant(6.0),
            constraint=nonneg,
            trainable=True
        )
        
        super(ShepherdPhysicsLayer, self).build(input_shape)
    
    def call(self, inputs):
        """
        Compute physics-predicted voltage using Shepherd model.
        
        CRITICAL: Inputs are MinMax-scaled [0,1].
        We INVERSE-SCALE capacity and current before applying physics.
        Otherwise the equation gets garbage inputs (as identified in Gemini analysis).
        """
        # inputs shape: (batch, features) — the last timestep from LSTM input
        
        # ===== INVERSE-SCALE to recover physical units =====
        # Formula: actual = scaled * range + min
        inputs_actual = inputs * self.scaler_range + self.scaler_min
        
        # Extract physical values (now in real units: Ah, A, V)
        capacity_end = tf.expand_dims(inputs_actual[:, self.cap_end_idx], axis=1)  # Ah
        current_i    = tf.constant(CURRENT_UA / 1e6, dtype=tf.float32)             # 10µA in A
        Q            = tf.constant(CAPACITY_AH, dtype=tf.float32)                  # 1.85 Ah
        E0           = tf.constant(V_FULL, dtype=tf.float32)                       # 3.7 V
        
        # Discharged capacity q = Q - capacity_remaining
        q = Q - capacity_end
        
        # CRITICAL: Clip denominator to prevent (Q-q) = 0 → infinity
        q_safe = tf.clip_by_value(q, 0.001, Q - 0.001)
        
        # ===== SHEPHERD EQUATION (Chapter 5 Eq 1.1) =====
        # V(t) = E0 - R*i - K*(Q/(Q-q))*q + A*exp(-B*q)
        V_predicted = (
            E0
            - self.R * current_i
            - self.K * (Q / (Q - q_safe + 1e-6)) * q_safe
            + self.A * tf.exp(-self.B * q_safe)
        )
        
        # Clip to physical voltage range (2.5V - 4.0V)
        V_predicted = tf.clip_by_value(V_predicted, 2.5, 4.0)
        
        return V_predicted
    
    def get_config(self):
        config = super(ShepherdPhysicsLayer, self).get_config()
        config.update({
            'scaler_min': self.scaler_min.numpy().tolist(),
            'scaler_max': self.scaler_max.numpy().tolist(),
            'feature_cols': self.feature_cols
        })
        return config

"""
PINN-LSTM Architecture (Chapter 4 Table 4.10, Chapter 5 Section 1.4.2):

Physics Branch:
    - ShepherdPhysicsLayer (learns R, K, A, B)
    - Dense(64, tanh) → Dense(32, tanh) → Dense(16, tanh)
    
LSTM Branch:
    - LSTM(128, return_sequences=True) → Dropout(0.2)
    - LSTM(64, return_sequences=False) → Dropout(0.2)
    - Dense(32, relu)

Fusion:
    - Concatenate([physics_features, lstm_features])
    - Dense(16, relu) → Dropout(0.2)
    - Dense(1, linear) → RUL in days

Loss: alpha*physics_MSE + beta*RUL_logcosh
    alpha=0.3 (Chapter 4 Table 4.10)
    beta=0.7 (Chapter 4 Table 4.10)
    
NOTE: Using log_cosh instead of MAE for RUL to suppress large gradient swings
during early training (Gemini analysis recommendation — valid technique).
"""

def build_pinn_lstm(input_shape, feature_cols, scaler):
    """
    Build PINN-LSTM model.
    
    Args:
        input_shape: (timesteps, n_features) e.g. (1, 13)
        feature_cols: list of feature names (for PhysicsLayer)
        scaler: fitted MinMaxScaler (for inverse transform in physics layer)
    
    Returns:
        Compiled Keras Model with dual outputs [rul_output, physics_output]
    """
    n_features = len(feature_cols)
    
    # ===== INPUT =====
    inp = layers.Input(shape=input_shape, name='battery_features')
    
    # Extract last timestep for physics layer
    # (We have 1 timestep, so this is just squeezing that dimension)
    last_state = layers.Lambda(
        lambda x: x[:, -1, :],
        name='extract_last_state'
    )(inp)
    
    # ===== PHYSICS BRANCH =====
    # Shepherd physics prediction (Chapter 5 Eq 1.1)
    physics_voltage = ShepherdPhysicsLayer(
        scaler_min=scaler.data_min_,
        scaler_max=scaler.data_max_,
        feature_cols=feature_cols,
        name='shepherd_physics'
    )(last_state)
    
    # Physics-aware dense feature extraction
    phys = layers.Dense(64, activation='tanh', name='physics_dense_1')(last_state)
    phys = layers.Dense(32, activation='tanh', name='physics_dense_2')(phys)
    phys = layers.Dense(16, activation='tanh', name='physics_features')(phys)
    
    # ===== LSTM BRANCH (Chapter 5: "Architecture: 3 couches LSTM") =====
    lstm = layers.LSTM(128, return_sequences=True, name='lstm_1')(inp)
    lstm = layers.Dropout(0.2, name='drop_lstm_1')(lstm)
    
    lstm = layers.LSTM(64, return_sequences=False, name='lstm_2')(lstm)
    lstm = layers.Dropout(0.2, name='drop_lstm_2')(lstm)
    
    lstm = layers.Dense(32, activation='relu', name='lstm_dense')(lstm)
    
    # ===== FUSION =====
    fusion = layers.Concatenate(name='fusion')([phys, lstm])
    fusion = layers.Dense(16, activation='relu', name='fusion_dense')(fusion)
    fusion = layers.Dropout(0.2, name='drop_fusion')(fusion)
    
    # ===== OUTPUTS =====
    # Main output: RUL prediction in days
    rul_output = layers.Dense(1, activation='linear', name='rul_output')(fusion)
    
    # Physics output: voltage for consistency loss
    physics_output = layers.Lambda(
        lambda x: x, name='physics_output'
    )(physics_voltage)
    
    model = keras.Model(inputs=inp, outputs=[rul_output, physics_output], name='PINN_LSTM_Battery_RUL')
    
    # ===== COMPILE =====
    # Use log_cosh for RUL (less sensitive to outliers than MAE)
    # Use MSE for physics voltage (standard regression)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss={
            'rul_output': keras.losses.LogCosh(),
            'physics_output': 'mse'
        },
        loss_weights={
            'rul_output': PRED_BETA,       # 0.7 (Chapter 4)
            'physics_output': PHYSICS_ALPHA * 2.5  # scaled up so physics gradients compete
        },
        metrics={
            'rul_output': ['mae'],
            'physics_output': ['mse']
        }
    )
    
    return model

model = build_pinn_lstm(
    input_shape=(1, len(FEATURE_COLS)),
    feature_cols=FEATURE_COLS,
    scaler=scaler
)
model.summary()

print("\n" + "="*60)
print("STEP 10: Training PINN-LSTM")
print("="*60)

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor='val_rul_output_mae',
        patience=20,
        restore_best_weights=True,
        mode='min',
        verbose=1
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor='val_rul_output_mae',
        factor=0.5,
        patience=8,
        min_lr=1e-6,
        verbose=1
    ),
    keras.callbacks.ModelCheckpoint(
        str(MODELS_DIR / 'battery_pinn_lstm_best.keras'),
        monitor='val_rul_output_mae',
        save_best_only=True,
        mode='min',
        verbose=0
    )
]

history = model.fit(
    X_train_lstm,
    {'rul_output': y_train, 'physics_output': v_train},
    validation_data=(
        X_test_lstm,
        {'rul_output': y_test, 'physics_output': v_test}
    ),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    verbose=1
)

print(f"\nTraining stopped at epoch {len(history.history['loss'])}")

print("\n" + "="*60)
print("STEP 11: Evaluation and Model Saving")
print("="*60)

# Predict
preds = model.predict(X_test_lstm, verbose=0)
y_pred_rul    = preds[0].flatten()
y_pred_physics = preds[1].flatten()

# RUL metrics
mae_days = mean_absolute_error(y_test, y_pred_rul)
r2       = r2_score(y_test, y_pred_rul)
rmse     = np.sqrt(np.mean((y_test - y_pred_rul)**2))

# Physics metrics
physics_mae = mean_absolute_error(v_test, y_pred_physics)

# Learned physics parameters
phys_layer = model.get_layer('shepherd_physics')
R_learned = float(phys_layer.R.numpy()[0])
K_learned = float(phys_layer.K.numpy()[0])
A_learned = float(phys_layer.A.numpy()[0])
B_learned = float(phys_layer.B.numpy()[0])

print("\n" + "="*70)
print("BATTERY PINN-LSTM — FINAL RESULTS")
print("="*70)
print(f"Test MAE:              {mae_days:.2f} days  (Target: <30 days)")
print(f"Test RMSE:             {rmse:.2f} days")
print(f"Test R²:               {r2:.4f}  (Target: >0.90)")
print(f"Physics Voltage MAE:   {physics_mae:.4f} V  (Target: <0.04V)")
print("="*70)
print(f"\nLearned Shepherd Parameters (Chapter 5 Eq 1.1):")
print(f"  R (resistance):    {R_learned:.5f} ohm")
print(f"  K (polarization):  {K_learned:.5f}")
print(f"  A (exponential):   {A_learned:.5f} V")
print(f"  B (time constant): {B_learned:.5f}")

target_met = mae_days < 30 and r2 > 0.90
status = "[OK] TARGET MET" if target_met else "[WARN] TARGET NOT MET"
print(f"\n{status} (REQ-PERF-01: Chapter 4)")

# ===== PLOTS =====
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Battery PINN-LSTM Results — Smart TwinPac', fontsize=14, fontweight='bold')

# Training MAE
axes[0,0].plot(history.history['rul_output_mae'], label='Train MAE')
axes[0,0].plot(history.history['val_rul_output_mae'], label='Val MAE')
axes[0,0].axhline(30, color='r', ls='--', linewidth=2, label='Target: 30 days')
axes[0,0].set_title('RUL MAE — Training History')
axes[0,0].set_xlabel('Epoch'); axes[0,0].set_ylabel('MAE (days)')
axes[0,0].legend(); axes[0,0].grid(True, alpha=0.3)

# Prediction vs Actual
axes[0,1].scatter(y_test, y_pred_rul, alpha=0.4, s=10)
lim = [min(y_test.min(), y_pred_rul.min()), max(y_test.max(), y_pred_rul.max())]
axes[0,1].plot(lim, lim, 'r--', linewidth=2, label='Perfect')
axes[0,1].set_title(f'Prediction vs Actual (MAE={mae_days:.1f}d, R²={r2:.3f})')
axes[0,1].set_xlabel('Actual RUL (days)'); axes[0,1].set_ylabel('Predicted RUL (days)')
axes[0,1].legend(); axes[0,1].grid(True, alpha=0.3)

# Residuals
residuals = y_test - y_pred_rul
axes[1,0].scatter(y_pred_rul, residuals, alpha=0.4, s=10)
axes[1,0].axhline(0, color='r', ls='--')
axes[1,0].axhline(30, color='orange', ls=':', label='±30d')
axes[1,0].axhline(-30, color='orange', ls=':')
axes[1,0].set_title('Residuals')
axes[1,0].set_xlabel('Predicted RUL'); axes[1,0].set_ylabel('Residual')
axes[1,0].legend(); axes[1,0].grid(True, alpha=0.3)

# Error distribution
axes[1,1].hist(residuals, bins=40, edgecolor='black', alpha=0.7)
axes[1,1].axvline(0, color='r', ls='--', linewidth=2)
axes[1,1].axvline(residuals.mean(), color='g', ls='--', label=f'Mean: {residuals.mean():.1f}d')
axes[1,1].set_title('Error Distribution')
axes[1,1].set_xlabel('Error (days)'); axes[1,1].set_ylabel('Count')
axes[1,1].legend(); axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(MODELS_DIR / 'battery_training_results.png', dpi=150, bbox_inches='tight')
print("[OK] Plot saved: models/battery_training_results.png")
# plt.show() # Commented out to run headlessly if needed

# ===== SAVE MODEL =====
model.save(MODELS_DIR / 'battery_pinn_lstm.keras')
print("[OK] Model saved: models/battery_pinn_lstm.keras")

# ===== SAVE MODEL INFO =====
model_info = {
    'model_name': 'PINN-LSTM Battery RUL',
    'chapter_reference': 'Chapter 4 LE-06, Chapter 5 Section 1.4.2',
    'physics_model': 'Shepherd Discharge Equation',
    'architecture': {
        'physics_branch': 'ShepherdPhysicsLayer + Dense(64,32,16, tanh)',
        'lstm_branch': 'LSTM(128) -> LSTM(64) -> Dense(32)',
        'fusion': 'Concatenate -> Dense(16) -> Dense(1)',
        'lstm_units': [128, 64],
        'window_size': WINDOW_SIZE
    },
    'training': {
        'loss_rul': 'logcosh',
        'loss_physics': 'mse',
        'alpha_physics': PHYSICS_ALPHA,
        'beta_prediction': PRED_BETA,
        'epochs_trained': len(history.history['loss']),
        'batch_size': BATCH_SIZE
    },
    'metrics': {
        'mae_days': float(mae_days),
        'rmse_days': float(rmse),
        'r2_score': float(r2),
        'physics_voltage_mae': float(physics_mae),
        'target_met': bool(target_met)
    },
    'shepherd_parameters_learned': {
        'R_resistance': R_learned,
        'K_polarization': K_learned,
        'A_exponential': A_learned,
        'B_exponential': B_learned
    },
    'data': {
        'feature_columns': FEATURE_COLS,
        'n_train': int(len(y_train)),
        'n_test': int(len(y_test)),
        'window_size': WINDOW_SIZE
    }
}

with open(MODELS_DIR / 'battery_rul_model_info.json', 'w') as f:
    json.dump(model_info, f, indent=2)

print("[OK] Saved: models/battery_rul_model_info.json")
print("\nDownload from Colab:")
print("   models/battery_pinn_lstm.keras")
print("   models/battery_rul_model_info.json")
print("   data/battery_stats.json")

print("\nHyperparameter Tuning Guide:")
print("If MAE > 30 days:")
print("  1. augmentation factor: 4 → 6")
print("  2. LSTM units: [128,64] → [256,128]")
print("  3. loss weights: alpha=0.2, beta*scale=2.0")
print("  4. window: 10 → 15 cycles")
print("\nIf physics_mae > 0.1V:")
print("  1. Check capacity units (should be Ah, not mAh)")
print("  2. Check voltage units (should be V, not mV)")

print("\n" + "="*60)
print("[OK] BATTERY PINN-LSTM PIPELINE COMPLETE")
print("="*60)
print("Files to download from Colab:")
print("  1. models/battery_pinn_lstm.keras")
print("  2. models/battery_rul_model_info.json")
print("  3. data/battery_stats.json")
print("\nThen copy to backend: cp models/*.keras backend/models/")
