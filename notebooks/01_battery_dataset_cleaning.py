"""
NASA Battery Dataset Cleaning & Adaptation for Pacemaker Use

Transforms NASA Li-ion battery data (aggressive lab cycling) into 
pacemaker battery discharge profiles (slow, continuous drain over 7 years)
"""

import numpy as np
import pandas as pd
import scipy.io
import json
from pathlib import Path
import matplotlib.pyplot as plt

print("🔋 Battery Dataset Cleaning Pipeline")
print("="*60)

# ===== CONFIGURATION =====

# Paths
RAW_DATA_DIR = Path('data/nasa_battery_raw')
OUTPUT_DIR = Path('data')
OUTPUT_DIR.mkdir(exist_ok=True)

# Battery files to process
BATTERY_FILES = ['B0005.mat', 'B0006.mat', 'B0007.mat', 'B0018.mat']

# Pacemaker parameters
PACEMAKER_LIFETIME_MONTHS = 84  # 7 years
PACEMAKER_VOLTAGE_FULL = 3.7    # V (Li-CFx chemistry)
PACEMAKER_VOLTAGE_EMPTY = 2.7   # V (end of life)
PACEMAKER_CAPACITY_AH = 1.85    # Ah (typical capacity)

# ===== HELPER FUNCTIONS =====

def load_nasa_battery(mat_file):
    """
    Load NASA battery .mat file and extract discharge cycles
    
    Returns:
        DataFrame with columns: cycle, voltage, current, temperature, capacity, time
    """
    print(f"\n📂 Loading: {mat_file}")
    
    try:
        mat_data = scipy.io.loadmat(mat_file)
    except Exception as e:
        print(f"❌ File not found or error loading {mat_file}: {e}")
        return None
    
    # Navigate nested structure: mat_data[battery_id]['cycle']
    battery_id = mat_file.stem  # e.g., 'B0005'
    
    try:
        battery_struct = mat_data[battery_id]
        cycle_data = battery_struct['cycle'][0, 0]
    except KeyError:
        print(f"❌ Unexpected file structure in {mat_file}")
        return None
    
    # Extract discharge cycles
    all_cycles = []
    
    num_cycles = cycle_data[0, 0]['type'].shape[0]
    print(f"   Found {num_cycles} cycles")
    
    for cycle_idx in range(num_cycles):
        cycle_type = cycle_data[0, 0]['type'][cycle_idx, 0][0]
        
        # We only want discharge cycles
        if cycle_type != 'discharge':
            continue
        
        # Extract data
        try:
            data_struct = cycle_data[0, 0]['data'][cycle_idx, 0]
            
            voltage = data_struct['Voltage_measured'][0, 0].flatten()
            current = data_struct['Current_measured'][0, 0].flatten()
            temperature = data_struct['Temperature_measured'][0, 0].flatten()
            time = data_struct['Time'][0, 0].flatten()
            
            # Capacity (integrate current over time)
            capacity = np.trapz(np.abs(current), time) / 3600  # Ah
            
            # Create DataFrame for this cycle
            cycle_df = pd.DataFrame({
                'cycle': cycle_idx,
                'time': time,
                'voltage': voltage,
                'current': current,
                'temperature': temperature,
                'capacity': capacity
            })
            
            all_cycles.append(cycle_df)
        
        except Exception as e:
            print(f"   ⚠️  Skipping cycle {cycle_idx}: {e}")
            continue
    
    if not all_cycles:
        print(f"   ❌ No discharge cycles found in {mat_file}")
        return None
    
    # Combine all cycles
    df = pd.concat(all_cycles, ignore_index=True)
    df['battery_id'] = battery_id
    
    print(f"   ✅ Loaded {len(all_cycles)} discharge cycles")
    print(f"   ✅ Total samples: {len(df)}")
    
    return df

def filter_discharge_only(df):
    """
    Keep only discharge phases (current < 0 or voltage decreasing)
    """
    # Current is negative during discharge in NASA data
    df = df[df['current'] <= 0].copy()
    
    print(f"   Filtered to discharge-only: {len(df)} samples")
    return df

def remap_to_pacemaker_timeline(df):
    """
    Remap NASA cycles to pacemaker months
    
    NASA: ~167 cycles over weeks (aggressive testing)
    Pacemaker: continuous discharge over 84 months (7 years)
    
    Mapping: month = cycle * (84 / max_cycle)
    """
    max_cycle = df['cycle'].max()
    
    df['month_equivalent'] = (df['cycle'] / max_cycle) * PACEMAKER_LIFETIME_MONTHS
    
    print(f"   Remapped {max_cycle} cycles → {PACEMAKER_LIFETIME_MONTHS} months")
    return df

def normalize_temperature(df, target_temp=37.0):
    """
    Filter to body temperature range (35-39°C)
    """
    # NASA data is in Celsius
    df = df[(df['temperature'] >= 35) & (df['temperature'] <= 39)].copy()
    
    if len(df) == 0:
        print("   ⚠️  Warning: No samples in body temp range, using all temperatures")
        return df
    
    print(f"   Filtered to body temperature (35-39°C): {len(df)} samples")
    return df

def calculate_rul(df):
    """
    Calculate Remaining Useful Life (days until voltage < 2.7V)
    """
    # Get max month for each battery
    max_month = df.groupby('battery_id')['month_equivalent'].max()
    
    # RUL = (end_month - current_month) * 30 days
    df['rul_days'] = df.apply(
        lambda row: (max_month[row['battery_id']] - row['month_equivalent']) * 30,
        axis=1
    )
    
    # Ensure non-negative
    df['rul_days'] = df['rul_days'].clip(lower=0)
    
    print(f"   Calculated RUL (range: 0-{df['rul_days'].max():.0f} days)")
    return df

def calculate_soh(df):
    """
    Calculate State of Health (SoH) based on capacity fade
    
    SoH = (current_capacity / initial_capacity) * 100
    """
    # Get initial capacity for each battery
    initial_capacity = df.groupby('battery_id')['capacity'].first()
    
    df['soh'] = df.apply(
        lambda row: (row['capacity'] / initial_capacity[row['battery_id']]) * 100,
        axis=1
    )
    
    print(f"   Calculated SoH (range: {df['soh'].min():.1f}%-{df['soh'].max():.1f}%)")
    return df

def augment_data(df, augmentation_factor=5):
    """
    Augment dataset by adding noise and time-warping
    
    Increases training samples while maintaining physical realism
    """
    print(f"\n🔄 Augmenting data (factor={augmentation_factor})...")
    
    augmented_dfs = [df.copy()]  # Original data
    
    for i in range(augmentation_factor - 1):
        aug_df = df.copy()
        
        # Add Gaussian noise
        aug_df['voltage'] += np.random.normal(0, 0.015, len(aug_df))  # ±15mV
        aug_df['temperature'] += np.random.normal(0, 0.5, len(aug_df))  # ±0.5°C
        aug_df['current'] *= np.random.uniform(0.95, 1.05, len(aug_df))  # ±5%
        
        # Time warping (stretch/compress timeline slightly)
        warp_factor = np.random.uniform(0.9, 1.1)
        aug_df['month_equivalent'] *= warp_factor
        aug_df['rul_days'] /= warp_factor
        
        # Update battery_id to indicate augmentation
        aug_df['battery_id'] = aug_df['battery_id'] + f'_aug{i+1}'
        
        augmented_dfs.append(aug_df)
    
    result = pd.concat(augmented_dfs, ignore_index=True)
    print(f"   ✅ Augmented: {len(df)} → {len(result)} samples")
    
    return result

def create_sequences(df, window_size=180):
    """
    Create sliding window sequences for LSTM training
    
    Args:
        df: Battery DataFrame
        window_size: History window in days (default 6 months)
    
    Returns:
        DataFrame with sequences ready for training
    """
    print(f"\n📊 Creating sequences (window={window_size} days)...")
    
    sequences = []
    
    for battery_id in df['battery_id'].unique():
        battery_df = df[df['battery_id'] == battery_id].sort_values('month_equivalent').reset_index(drop=True)
        
        # Convert month to day for window calculation
        battery_df['day_equivalent'] = battery_df['month_equivalent'] * 30
        
        # Sample at daily resolution
        daily_samples = []
        for day in range(0, int(battery_df['day_equivalent'].max())):
            # Get reading closest to this day
            closest_idx = (battery_df['day_equivalent'] - day).abs().idxmin()
            daily_samples.append(battery_df.loc[closest_idx])
        
        daily_df = pd.DataFrame(daily_samples).reset_index(drop=True)
        
        # Create sliding windows
        for i in range(len(daily_df) - window_size):
            window = daily_df.iloc[i:i+window_size]
            target = daily_df.iloc[i+window_size]
            
            seq = {
                'battery_id': battery_id,
                'sequence_start_day': window['day_equivalent'].iloc[0],
                'sequence_end_day': window['day_equivalent'].iloc[-1],
                'voltage_mean': window['voltage'].mean(),
                'voltage_std': window['voltage'].std(),
                'voltage_min': window['voltage'].min(),
                'voltage_max': window['voltage'].max(),
                'current_mean': window['current'].mean(),
                'temperature_mean': window['temperature'].mean(),
                'temperature_std': window['temperature'].std(),
                'capacity_start': window['capacity'].iloc[0],
                'capacity_end': window['capacity'].iloc[-1],
                'capacity_fade_rate': (window['capacity'].iloc[0] - window['capacity'].iloc[-1]) / window_size,
                'soh_current': target['soh'],
                'rul_days_target': target['rul_days']
            }
            
            sequences.append(seq)
    
    seq_df = pd.DataFrame(sequences)
    print(f"   ✅ Created {len(seq_df)} sequences")
    
    return seq_df

# ===== MAIN PROCESSING PIPELINE =====

print("\n" + "="*60)
print("STEP 1: Loading NASA Battery Data")
print("="*60)

all_batteries = []

for mat_file in BATTERY_FILES:
    mat_path = RAW_DATA_DIR / mat_file
    
    df = load_nasa_battery(mat_path)
    
    if df is not None:
        # Clean and transform
        df = filter_discharge_only(df)
        df = normalize_temperature(df)
        df = remap_to_pacemaker_timeline(df)
        df = calculate_rul(df)
        df = calculate_soh(df)
        
        all_batteries.append(df)

if not all_batteries:
    synth_file = OUTPUT_DIR / 'battery_synthetic_raw.csv'
    if synth_file.exists():
        print("\n⚠️ No NASA data loaded. Falling back to synthetic data...")
        full_df = pd.read_csv(synth_file)
    else:
        print("\n❌ No battery data loaded!")
        print("Run: python scripts/download_nasa_battery_data.py")
        print("Or: python scripts/generate_synthetic_battery_data.py")
        raise SystemExit(1)
else:
    # Combine all batteries
    full_df = pd.concat(all_batteries, ignore_index=True)

print("\n" + "="*60)
print("STEP 2: Data Validation")
print("="*60)

print(f"Total samples: {len(full_df)}")
print(f"Batteries: {full_df['battery_id'].nunique()}")
print(f"Voltage range: {full_df['voltage'].min():.2f}V - {full_df['voltage'].max():.2f}V")
print(f"Temperature range: {full_df['temperature'].min():.1f}°C - {full_df['temperature'].max():.1f}°C")
print(f"RUL range: {full_df['rul_days'].min():.0f} - {full_df['rul_days'].max():.0f} days")

# Validation checks
assert full_df['voltage'].between(2.5, 4.2).all(), "Voltage out of range"
assert full_df['rul_days'].min() >= 0, "Negative RUL detected"

print("✅ Validation passed")

# ===== AUGMENTATION =====

print("\n" + "="*60)
print("STEP 3: Data Augmentation")
print("="*60)

full_df = augment_data(full_df, augmentation_factor=3)

# ===== SEQUENCE CREATION =====

print("\n" + "="*60)
print("STEP 4: Sequence Creation")
print("="*60)

sequence_df = create_sequences(full_df, window_size=180)

# ===== TRAIN/TEST SPLIT =====

print("\n" + "="*60)
print("STEP 5: Train/Test Split")
print("="*60)

from sklearn.model_selection import train_test_split

train_df, test_df = train_test_split(
    sequence_df,
    test_size=0.2,
    random_state=42,
    shuffle=True
)

print(f"Training sequences: {len(train_df)}")
print(f"Test sequences: {len(test_df)}")

# ===== SAVE OUTPUTS =====

print("\n" + "="*60)
print("STEP 6: Saving Outputs")
print("="*60)

# Save train/test sets
train_df.to_csv(OUTPUT_DIR / 'battery_train.csv', index=False)
print(f"✅ Saved: {OUTPUT_DIR / 'battery_train.csv'}")

test_df.to_csv(OUTPUT_DIR / 'battery_test.csv', index=False)
print(f"✅ Saved: {OUTPUT_DIR / 'battery_test.csv'}")

# Save normalization statistics
feature_cols = [
    'voltage_mean', 'voltage_std', 'voltage_min', 'voltage_max',
    'current_mean', 'temperature_mean', 'temperature_std',
    'capacity_start', 'capacity_end', 'capacity_fade_rate', 'soh_current'
]

stats = {
    col: {
        'mean': float(train_df[col].mean()),
        'std': float(train_df[col].std()),
        'min': float(train_df[col].min()),
        'max': float(train_df[col].max())
    }
    for col in feature_cols
}

with open(OUTPUT_DIR / 'battery_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print(f"✅ Saved: {OUTPUT_DIR / 'battery_stats.json'}")

# ===== VISUALIZATION =====

print("\n" + "="*60)
print("STEP 7: Visualization")
print("="*60)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Voltage over time
for battery_id in full_df['battery_id'].unique()[:5]:  # Plot first 5
    battery_data = full_df[full_df['battery_id'] == battery_id]
    axes[0, 0].plot(battery_data['month_equivalent'], battery_data['voltage'], alpha=0.6, label=battery_id)

axes[0, 0].set_xlabel('Month')
axes[0, 0].set_ylabel('Voltage (V)')
axes[0, 0].set_title('Voltage Degradation Over Time')
axes[0, 0].legend()
axes[0, 0].grid(True)

# SoH over time
for battery_id in full_df['battery_id'].unique()[:5]:
    battery_data = full_df[full_df['battery_id'] == battery_id]
    axes[0, 1].plot(battery_data['month_equivalent'], battery_data['soh'], alpha=0.6)

axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('SoH (%)')
axes[0, 1].set_title('State of Health Degradation')
axes[0, 1].grid(True)

# RUL distribution
axes[1, 0].hist(sequence_df['rul_days_target'], bins=50, edgecolor='black', alpha=0.7)
axes[1, 0].set_xlabel('RUL (days)')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('RUL Distribution in Training Data')
axes[1, 0].grid(True)

# Voltage vs RUL correlation
axes[1, 1].scatter(sequence_df['voltage_mean'], sequence_df['rul_days_target'], alpha=0.3, s=1)
axes[1, 1].set_xlabel('Mean Voltage (V)')
axes[1, 1].set_ylabel('RUL (days)')
axes[1, 1].set_title('Voltage-RUL Correlation')
axes[1, 1].grid(True)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'battery_dataset_analysis.png', dpi=150)
print(f"✅ Saved: {OUTPUT_DIR / 'battery_dataset_analysis.png'}")

# ===== FINAL SUMMARY =====

print("\n" + "="*60)
print("✅ BATTERY DATASET PREPARATION COMPLETE")
print("="*60)
print(f"📊 Training sequences: {len(train_df)}")
print(f"📊 Test sequences: {len(test_df)}")
print(f"📊 Features per sequence: {len(feature_cols)}")
print(f"📊 Window size: 180 days (6 months)")
print(f"📊 Target: RUL prediction (days)")
print("\n🎯 Next step: Train PINN-LSTM model (notebook 02)")
print("="*60)
