"""
Metabolic Dataset Generation using Bergman Minimal Model

Generates realistic glucose-insulin dynamics for 10,000 virtual patients
with varying insulin sensitivity, meal patterns, and exercise events.
"""

import numpy as np
import pandas as pd
from scipy.integrate import odeint
import json
from pathlib import Path
import matplotlib.pyplot as plt

print("🍬 Metabolic Dataset Generator (Bergman Minimal Model)")
print("="*60)

# ===== BERGMAN MODEL PARAMETERS =====

# Normal ranges for patient-specific parameters
PARAM_RANGES = {
    'SI': (0.2, 0.5),      # Insulin sensitivity (1/(mU/L·min))
    'SG': (0.015, 0.03),   # Glucose effectiveness (1/min)
    'p2': (0.02, 0.03),    # Rate of insulin action decay (1/min)
    'p3': (1e-5, 3e-5),    # Insulin action on glucose uptake (mU/L)
    'n': (0.15, 0.25),     # Insulin decay rate (1/min)
    'gamma': (0.003, 0.008) # Pancreatic response (mU/(L·mg/dL·min))
}

# Basal values
GLUCOSE_BASAL = 90  # mg/dL
INSULIN_BASAL = 10  # µU/mL

# ===== BERGMAN MINIMAL MODEL =====

def bergman_model(y, t, SI, SG, p2, p3, n, gamma, meal_schedule, exercise_schedule):
    """
    Bergman Minimal Model for glucose-insulin dynamics
    
    State variables:
        y[0] = G: Blood glucose (mg/dL)
        y[1] = X: Insulin action on glucose (1/min)
        y[2] = I: Plasma insulin (µU/mL)
    
    Parameters:
        SI: Insulin sensitivity
        SG: Glucose effectiveness
        p2: Insulin action decay rate
        p3: Insulin action increase per unit insulin
        n: Insulin decay rate
        gamma: Pancreatic responsiveness
    
    External inputs:
        meal_schedule: List of (time_min, carbs_g)
        exercise_schedule: List of (time_min, intensity)
    
    ODEs:
        dG/dt = -SG·G - X·G + D(t)
        dX/dt = -p2·X + p3·(I - Ib)
        dI/dt = -n·(I - Ib) + γ·max(0, G - Gb)
    
    where:
        D(t) = meal glucose absorption rate
        Ib = basal insulin
        Gb = basal glucose
    """
    G, X, I = y
    
    Gb = GLUCOSE_BASAL
    Ib = INSULIN_BASAL
    
    # ===== MEAL ABSORPTION =====
    # Gaussian absorption profile: peaks at 30min, duration ~90min
    D = 0
    for meal_time, carbs in meal_schedule:
        time_since_meal = t - meal_time
        
        if 0 <= time_since_meal <= 120:  # 2h absorption window
            # Gaussian absorption (peak at 30min)
            absorption_rate = (carbs / 30) * np.exp(-((time_since_meal - 30)**2) / 400)
            D += absorption_rate
    
    # ===== EXERCISE EFFECT =====
    # Exercise increases glucose uptake (equivalent to negative glucose input)
    E = 0
    for exercise_time, intensity in exercise_schedule:
        time_since_exercise = t - exercise_time
        
        if 0 <= time_since_exercise <= 60:  # 1h effect
            # Exponential decay of exercise effect
            E += intensity * 2 * np.exp(-time_since_exercise / 30)  # mg/dL/min
    
    # ===== ODEs =====
    dG = -SG * (G - Gb) - X * G + D - E
    dX = -p2 * X + p3 * (I - Ib)
    dI = -n * (I - Ib) + gamma * max(0, G - Gb)
    
    return [dG, dX, dI]

# ===== PATIENT PROFILE GENERATOR =====

def generate_patient_parameters():
    """
    Generate random patient with physiological parameters
    
    Returns:
        dict with SI, SG, p2, p3, n, gamma
    """
    params = {}
    for key, (min_val, max_val) in PARAM_RANGES.items():
        params[key] = np.random.uniform(min_val, max_val)
    
    return params

def generate_meal_schedule():
    """
    Generate realistic meal schedule for 24h
    
    Returns:
        List of (time_min, carbs_g) tuples
    """
    meals = []
    
    # Breakfast (7-9am)
    breakfast_time = np.random.uniform(420, 540)  # 7-9h in minutes
    breakfast_carbs = np.random.uniform(50, 80)
    meals.append((breakfast_time, breakfast_carbs))
    
    # Lunch (12-2pm)
    lunch_time = np.random.uniform(720, 840)
    lunch_carbs = np.random.uniform(60, 90)
    meals.append((lunch_time, lunch_carbs))
    
    # Dinner (6-8pm)
    dinner_time = np.random.uniform(1080, 1200)
    dinner_carbs = np.random.uniform(70, 100)
    meals.append((dinner_time, dinner_carbs))
    
    # Optional snack (50% chance)
    if np.random.rand() > 0.5:
        snack_time = np.random.choice([600, 960, 1320])  # 10am, 4pm, 10pm
        snack_carbs = np.random.uniform(15, 30)
        meals.append((snack_time, snack_carbs))
    
    return meals

def generate_exercise_schedule():
    """
    Generate exercise events (30% of patients exercise)
    
    Returns:
        List of (time_min, intensity) tuples
    """
    if np.random.rand() > 0.3:
        return []  # No exercise
    
    # Exercise time (morning or evening)
    if np.random.rand() > 0.5:
        exercise_time = np.random.uniform(360, 480)  # 6-8am
    else:
        exercise_time = np.random.uniform(1020, 1140)  # 5-7pm
    
    # Intensity (0.5 = light, 1.0 = moderate, 1.5 = vigorous)
    intensity = np.random.choice([0.5, 1.0, 1.5], p=[0.5, 0.4, 0.1])
    
    return [(exercise_time, intensity)]

def simulate_patient_day(patient_id, params, meals, exercise):
    """
    Simulate 24h glucose-insulin dynamics for one patient
    
    Args:
        patient_id: Patient identifier
        params: Bergman model parameters
        meals: Meal schedule
        exercise: Exercise schedule
    
    Returns:
        DataFrame with minute-by-minute glucose, insulin data
    """
    # Time vector (0-1440 minutes = 24 hours)
    t = np.linspace(0, 1440, 1440)
    
    # Initial conditions [G, X, I]
    y0 = [GLUCOSE_BASAL, 0, INSULIN_BASAL]
    
    # Solve ODEs
    solution = odeint(
        bergman_model,
        y0,
        t,
        args=(
            params['SI'], params['SG'], params['p2'],
            params['p3'], params['n'], params['gamma'],
            meals, exercise
        )
    )
    
    # Extract solution
    glucose = solution[:, 0]
    insulin_action = solution[:, 1]
    insulin = solution[:, 2]
    
    # Create DataFrame
    df = pd.DataFrame({
        'patient_id': patient_id,
        'time_min': t,
        'glucose': glucose,
        'insulin_action': insulin_action,
        'insulin': insulin,
    })
    
    # Add meal/exercise flags
    df['time_since_meal'] = 999.0
    for meal_time, _ in meals:
        mask = df['time_min'] >= meal_time
        df.loc[mask, 'time_since_meal'] = np.minimum(
            df.loc[mask, 'time_since_meal'],
            df.loc[mask, 'time_min'] - meal_time
        )
    
    df['exercise_active'] = 0
    for exercise_time, _ in exercise:
        mask = (df['time_min'] >= exercise_time) & (df['time_min'] < exercise_time + 60)
        df.loc[mask, 'exercise_active'] = 1
    
    return df

# ===== DATASET GENERATION =====

print("\n" + "="*60)
print("STEP 1: Generating Patient Profiles")
print("="*60)

NUM_PATIENTS = 1000
all_data = []

for i in range(NUM_PATIENTS):
    patient_id = f'META_{i:05d}'
    
    # Generate patient characteristics
    params = generate_patient_parameters()
    meals = generate_meal_schedule()
    exercise = generate_exercise_schedule()
    
    # Simulate 24h
    patient_df = simulate_patient_day(patient_id, params, meals, exercise)
    
    all_data.append(patient_df)
    
    if (i + 1) % 1000 == 0:
        print(f"Generated {i+1}/{NUM_PATIENTS} patients...")

print(f"\n✅ Generated {NUM_PATIENTS} patient simulations")

# Combine all data
full_df = pd.concat(all_data, ignore_index=True)

print(f"Total datapoints: {len(full_df):,}")
print(f"Glucose range: {full_df['glucose'].min():.1f} - {full_df['glucose'].max():.1f} mg/dL")
print(f"Insulin range: {full_df['insulin'].min():.1f} - {full_df['insulin'].max():.1f} µU/mL")

# ===== CREATE SEQUENCES FOR LSTM =====

print("\n" + "="*60)
print("STEP 2: Creating LSTM Training Sequences")
print("="*60)

def create_sequences(df, history_window=120, prediction_horizon=60):
    """
    Create sliding window sequences for LSTM
    
    Args:
        df: Patient DataFrame
        history_window: Minutes of history to use (default 120 = 2h)
        prediction_horizon: Minutes ahead to predict (default 60 = 1h)
    
    Returns:
        DataFrame with sequences
    """
    sequences = []
    
    for patient_id in df['patient_id'].unique():
        patient_df = df[df['patient_id'] == patient_id].sort_values('time_min').reset_index(drop=True)
        
        # Sliding windows
        for i in range(len(patient_df) - history_window - prediction_horizon):
            history = patient_df.iloc[i:i+history_window]
            target = patient_df.iloc[i+history_window+prediction_horizon]
            
            seq = {
                'patient_id': patient_id,
                'sequence_start_time': history['time_min'].iloc[0],
                
                # History features (aggregated)
                'glucose_mean': history['glucose'].mean(),
                'glucose_std': history['glucose'].std(),
                'glucose_min': history['glucose'].min(),
                'glucose_max': history['glucose'].max(),
                'glucose_current': history['glucose'].iloc[-1],
                'glucose_trend': (history['glucose'].iloc[-1] - history['glucose'].iloc[0]) / history_window,
                
                'insulin_mean': history['insulin'].mean(),
                'insulin_std': history['insulin'].std(),
                'insulin_current': history['insulin'].iloc[-1],
                
                'time_since_meal': history['time_since_meal'].iloc[-1],
                'exercise_active': history['exercise_active'].iloc[-1],
                
                # Target (1h ahead glucose)
                'target_glucose': target['glucose']
            }
            
            sequences.append(seq)
    
    return pd.DataFrame(sequences)

sequence_df = create_sequences(full_df, history_window=120, prediction_horizon=60)

print(f"✅ Created {len(sequence_df):,} sequences")
print(f"Features per sequence: {len(sequence_df.columns) - 2}")  # -2 for patient_id and target

# ===== VALIDATION =====

print("\n" + "="*60)
print("STEP 3: Data Validation")
print("="*60)

# Check for invalid values
assert sequence_df['target_glucose'].between(40, 400).all(), "Target glucose out of range"
assert not sequence_df.isnull().any().any(), "Null values detected"

print("✅ Data validation passed")

print("\nTarget glucose statistics:")
print(sequence_df['target_glucose'].describe())

# ===== TRAIN/TEST SPLIT =====

print("\n" + "="*60)
print("STEP 4: Train/Test Split")
print("="*60)

from sklearn.model_selection import train_test_split

train_df, test_df = train_test_split(
    sequence_df,
    test_size=0.2,
    random_state=42,
    shuffle=True
)

print(f"Training sequences: {len(train_df):,}")
print(f"Test sequences: {len(test_df):,}")

# ===== SAVE OUTPUTS =====

print("\n" + "="*60)
print("STEP 5: Saving Outputs")
print("="*60)

output_dir = Path('data')
output_dir.mkdir(exist_ok=True)

# Save train/test
train_df.to_csv(output_dir / 'metabolic_train.csv', index=False)
print(f"✅ Saved: {output_dir / 'metabolic_train.csv'}")

test_df.to_csv(output_dir / 'metabolic_test.csv', index=False)
print(f"✅ Saved: {output_dir / 'metabolic_test.csv'}")

# Save normalization stats
feature_cols = [
    'glucose_mean', 'glucose_std', 'glucose_min', 'glucose_max',
    'glucose_current', 'glucose_trend',
    'insulin_mean', 'insulin_std', 'insulin_current',
    'time_since_meal', 'exercise_active'
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

with open(output_dir / 'metabolic_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print(f"✅ Saved: {output_dir / 'metabolic_stats.json'}")

# ===== VISUALIZATION =====

print("\n" + "="*60)
print("STEP 6: Visualization")
print("="*60)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Sample patient glucose profile
sample_patient = full_df[full_df['patient_id'] == 'META_00000']
axes[0, 0].plot(sample_patient['time_min'] / 60, sample_patient['glucose'], linewidth=2)
axes[0, 0].axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Hypoglycemia (70)')
axes[0, 0].axhline(y=180, color='orange', linestyle='--', alpha=0.5, label='Hyperglycemia (180)')
axes[0, 0].set_xlabel('Time (hours)')
axes[0, 0].set_ylabel('Glucose (mg/dL)')
axes[0, 0].set_title('Sample Patient: 24h Glucose Profile')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Glucose distribution
axes[0, 1].hist(full_df['glucose'], bins=50, edgecolor='black', alpha=0.7)
axes[0, 1].axvline(x=70, color='r', linestyle='--', linewidth=2)
axes[0, 1].axvline(x=180, color='orange', linestyle='--', linewidth=2)
axes[0, 1].set_xlabel('Glucose (mg/dL)')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].set_title('Glucose Distribution Across All Patients')
axes[0, 1].grid(True, alpha=0.3)

# Target glucose distribution
axes[1, 0].hist(sequence_df['target_glucose'], bins=50, edgecolor='black', alpha=0.7)
axes[1, 0].set_xlabel('Target Glucose (mg/dL)')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Prediction Target Distribution (1h ahead)')
axes[1, 0].grid(True, alpha=0.3)

# Current vs target glucose
axes[1, 1].scatter(
    sequence_df['glucose_current'], 
    sequence_df['target_glucose'], 
    alpha=0.1, 
    s=1
)
axes[1, 1].plot([40, 400], [40, 400], 'r--', linewidth=2, label='Perfect prediction')
axes[1, 1].set_xlabel('Current Glucose (mg/dL)')
axes[1, 1].set_ylabel('Target Glucose (1h ahead)')
axes[1, 1].set_title('Current vs Future Glucose Correlation')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / 'metabolic_dataset_analysis.png', dpi=150)
print(f"✅ Saved: {output_dir / 'metabolic_dataset_analysis.png'}")

# ===== FINAL SUMMARY =====

print("\n" + "="*60)
print("✅ METABOLIC DATASET GENERATION COMPLETE")
print("="*60)
print(f"📊 Total patients: {NUM_PATIENTS}")
print(f"📊 Total datapoints: {len(full_df):,}")
print(f"📊 Training sequences: {len(train_df):,}")
print(f"📊 Test sequences: {len(test_df):,}")
print(f"📊 Features: {len(feature_cols)}")
print(f"📊 Prediction horizon: 60 minutes")
print("\n🎯 Next step: Train Stacked LSTM (notebook 06)")
print("="*60)
