"""
Synthetic Battery Data Generator (Fallback)

Generates realistic battery degradation curves if NASA data is unavailable
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path

def shepherd_model(t, E0=3.7, R=0.1, K=0.01, Q=1.85, A=0.2, B=5):
    """
    Shepherd battery discharge model
    
    V(t) = E0 - R*i - K*(Q/(Q-q))*q + A*exp(-B*q)
    
    Simplified for constant current discharge
    """
    q = t * 0.00001 * 24  # Discharged capacity (Ah) over time (days)
    i = 0.00001  # Constant 10µA discharge
    
    # Voltage drops as capacity depletes
    voltage = E0 - R * i - K * (Q / (Q - q + 0.01)) * q + A * np.exp(-B * q)
    
    return voltage

def generate_synthetic_battery(battery_id, num_days=2520, noise_level=0.02):
    """
    Generate one synthetic battery degradation curve
    """
    days = np.linspace(0, num_days, num_days)
    
    # Base degradation curve
    voltage = shepherd_model(days)
    
    # Add realistic noise
    voltage += np.random.normal(0, noise_level, len(days))
    
    # Temperature (body temp with small variation)
    temperature = 37 + np.random.normal(0, 0.5, len(days))
    
    # Current (constant discharge with pulses)
    current = -0.00001 * np.ones(len(days))
    
    # Capacity fade
    initial_capacity = 1.85
    capacity = initial_capacity * (1 - days / num_days * 0.2)  # 20% fade over lifetime
    
    # SoH
    soh = (capacity / initial_capacity) * 100
    
    # RUL
    rul_days = num_days - days
    
    # Month equivalent
    month_equivalent = days / 30
    
    df = pd.DataFrame({
        'battery_id': battery_id,
        'cycle': np.arange(len(days)),
        'month_equivalent': month_equivalent,
        'voltage': voltage,
        'current': current,
        'temperature': temperature,
        'capacity': capacity,
        'soh': soh,
        'rul_days': rul_days,
        'time': days * 24 * 3600  # seconds
    })
    
    return df

print("🔋 Generating Synthetic Battery Data (Fallback)")
print("="*60)

output_dir = Path('data')
output_dir.mkdir(exist_ok=True)

# Generate 10 synthetic batteries
all_batteries = []

for i in range(10):
    battery_id = f'SYNTH_{i:03d}'
    print(f"Generating {battery_id}...")
    
    df = generate_synthetic_battery(battery_id, num_days=2520, noise_level=0.015)
    all_batteries.append(df)

full_df = pd.concat(all_batteries, ignore_index=True)

print(f"\n✅ Generated {len(full_df)} samples from {len(all_batteries)} batteries")

# Save raw data
full_df.to_csv(output_dir / 'battery_synthetic_raw.csv', index=False)
print(f"✅ Saved: {output_dir / 'battery_synthetic_raw.csv'}")

print("\n🎯 Now run: python notebooks/01_battery_dataset_cleaning.py")
print("   (It will process synthetic data if NASA data is unavailable)")
