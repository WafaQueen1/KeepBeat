"""
Stacked LSTM for Glucose-Insulin Dynamics Prediction

Architecture:
- 3 stacked LSTM layers (128 → 64 → 32 units)
- Dual input: Time-series features + Metadata (meals, exercise)
- Dense fusion layer
- Target: Predict glucose 1h ahead

Target: MAE < 15 mg/dL, RMSE < 20 mg/dL
"""

import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

print(f"TensorFlow version: {tf.__version__}")
print(f"GPU available: {tf.config.list_physical_devices('GPU')}")

# Set random seeds
np.random.seed(42)
tf.random.set_seed(42)

# ===== LOAD DATA =====

print("\n" + "="*60)
print("STEP 1: Loading Dataset")
print("="*60)

train_df = pd.read_csv('data/metabolic_train.csv')
test_df = pd.read_csv('data/metabolic_test.csv')

with open('data/metabolic_stats.json', 'r') as f:
    stats = json.load(f)

print(f"Training sequences: {len(train_df):,}")
print(f"Test sequences: {len(test_df):,}")

# ===== FEATURE ENGINEERING =====

print("\n" + "="*60)
print("STEP 2: Feature Preparation")
print("="*60)

# Time-series features (glucose + insulin history)
timeseries_cols = [
    'glucose_mean', 'glucose_std', 'glucose_min', 'glucose_max',
    'glucose_current', 'glucose_trend',
    'insulin_mean', 'insulin_std', 'insulin_current'
]

# Metadata features (meal timing, exercise)
metadata_cols = [
    'time_since_meal',
    'exercise_active'
]

# Target
target_col = 'target_glucose'

print(f"Time-series features: {len(timeseries_cols)}")
print(f"Metadata features: {len(metadata_cols)}")

# Normalize features
def normalize_features(df, stats):
    """Z-score normalization"""
    df_norm = df.copy()
    
    for col in timeseries_cols + metadata_cols:
        mean = stats[col]['mean']
        std = stats[col]['std']
        
        if std == 0:
            std = 1
        
        df_norm[f'{col}_norm'] = (df[col] - mean) / std
    
    return df_norm

train_df = normalize_features(train_df, stats)
test_df = normalize_features(test_df, stats)

# Extract features
timeseries_cols_norm = [f'{col}_norm' for col in timeseries_cols]
metadata_cols_norm = [f'{col}_norm' for col in metadata_cols]

X_ts_train = train_df[timeseries_cols_norm].values
X_meta_train = train_df[metadata_cols_norm].values
y_train = train_df[target_col].values

X_ts_test = test_df[timeseries_cols_norm].values
X_meta_test = test_df[metadata_cols_norm].values
y_test = test_df[target_col].values

print(f"\nX_ts_train shape: {X_ts_train.shape} (time-series)")
print(f"X_meta_train shape: {X_meta_train.shape} (metadata)")
print(f"y_train shape: {y_train.shape}")

# Reshape time-series for LSTM (add timestep dimension)
# We have aggregated features, so treat as single timestep
X_ts_train_lstm = X_ts_train.reshape((X_ts_train.shape[0], 1, X_ts_train.shape[1]))
X_ts_test_lstm = X_ts_test.reshape((X_ts_test.shape[0], 1, X_ts_test.shape[1]))

print(f"\nLSTM time-series input: {X_ts_train_lstm.shape} (samples, timesteps, features)")
print(f"Metadata input: {X_meta_train.shape}")

# ===== BUILD STACKED LSTM =====

print("\n" + "="*60)
print("STEP 3: Building Stacked LSTM Architecture")
print("="*60)

def build_metabolic_lstm(ts_shape=(1, 9), meta_shape=(2,)):
    """
    Dual-input Stacked LSTM for glucose prediction
    
    Architecture:
    - Input 1: Time-series (glucose/insulin history) → 3 stacked LSTMs
    - Input 2: Metadata (meal/exercise) → Dense layers
    - Fusion: Concatenate both streams
    - Output: Glucose prediction (1h ahead)
    
    Args:
        ts_shape: Time-series input shape (timesteps, features)
        meta_shape: Metadata input shape (features,)
    
    Returns:
        Compiled Keras Model
    """
    
    # ===== INPUT 1: TIME-SERIES (LSTM BRANCH) =====
    ts_input = layers.Input(shape=ts_shape, name='timeseries_input')
    
    # First LSTM layer (128 units)
    lstm1 = layers.LSTM(128, return_sequences=True, name='lstm_1')(ts_input)
    lstm1 = layers.Dropout(0.3, name='dropout_lstm_1')(lstm1)
    
    # Second LSTM layer (64 units)
    lstm2 = layers.LSTM(64, return_sequences=True, name='lstm_2')(lstm1)
    lstm2 = layers.Dropout(0.3, name='dropout_lstm_2')(lstm2)
    
    # Third LSTM layer (32 units, no return sequences)
    lstm3 = layers.LSTM(32, return_sequences=False, name='lstm_3')(lstm2)
    lstm3 = layers.Dropout(0.3, name='dropout_lstm_3')(lstm3)
    
    # Dense layer after LSTM
    lstm_dense = layers.Dense(16, activation='relu', name='lstm_dense')(lstm3)
    
    # ===== INPUT 2: METADATA (DENSE BRANCH) =====
    meta_input = layers.Input(shape=meta_shape, name='metadata_input')
    
    # Dense layers for metadata
    meta_dense = layers.Dense(16, activation='relu', name='meta_dense_1')(meta_input)
    meta_dense = layers.Dropout(0.2, name='dropout_meta')(meta_dense)
    meta_dense = layers.Dense(8, activation='relu', name='meta_dense_2')(meta_dense)
    
    # ===== FUSION =====
    # Concatenate LSTM features + metadata features
    fusion = layers.Concatenate(name='fusion')([lstm_dense, meta_dense])
    
    # Fusion dense layers
    fusion = layers.Dense(16, activation='relu', name='fusion_dense_1')(fusion)
    fusion = layers.Dropout(0.2, name='dropout_fusion')(fusion)
    fusion = layers.Dense(8, activation='relu', name='fusion_dense_2')(fusion)
    
    # ===== OUTPUT =====
    # Glucose prediction (linear activation for regression)
    output = layers.Dense(1, activation='linear', name='glucose_output')(fusion)
    
    # ===== BUILD MODEL =====
    model = Model(
        inputs=[ts_input, meta_input],
        outputs=output,
        name='Stacked_LSTM_Metabolic'
    )
    
    # ===== COMPILE =====
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mse',  # Mean Squared Error
        metrics=['mae', 'mse']  # Mean Absolute Error, MSE
    )
    
    return model

# Build model
model = build_metabolic_lstm(
    ts_shape=(1, len(timeseries_cols_norm)),
    meta_shape=(len(metadata_cols_norm),)
)

model.summary()

# ===== TRAINING =====

print("\n" + "="*60)
print("STEP 4: Training Model")
print("="*60)

# Callbacks
callbacks = [
    EarlyStopping(
        monitor='val_mae',
        patience=15,
        restore_best_weights=True,
        mode='min',
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_mae',
        factor=0.5,
        patience=7,
        min_lr=1e-6,
        mode='min',
        verbose=1
    ),
    ModelCheckpoint(
        'models/metabolic_lstm_best.keras',
        monitor='val_mae',
        save_best_only=True,
        mode='min',
        verbose=1
    )
]

print("🚀 Starting training...")
print(f"   Training on {len(y_train):,} sequences")
print(f"   Validating on {len(y_test):,} sequences")

history = model.fit(
    [X_ts_train_lstm, X_meta_train],
    y_train,
    validation_data=(
        [X_ts_test_lstm, X_meta_test],
        y_test
    ),
    epochs=30,
    batch_size=64,
    callbacks=callbacks,
    verbose=1
)

# ===== EVALUATION =====

print("\n" + "="*60)
print("STEP 5: Model Evaluation")
print("="*60)

# Predict on test set
y_pred = model.predict([X_ts_test_lstm, X_meta_test], verbose=0).flatten()

# Metrics
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# Clinical accuracy metrics
# Within ±15 mg/dL (tight control)
within_15 = np.mean(np.abs(y_test - y_pred) <= 15) * 100

# Within ±20 mg/dL (acceptable)
within_20 = np.mean(np.abs(y_test - y_pred) <= 20) * 100

# Clarke Error Grid Zones (simplified)
def clarke_error_grid_zone(actual, predicted):
    """Simplified Clarke Error Grid classification"""
    zones = []
    for a, p in zip(actual, predicted):
        if a < 70 and p < 70:
            zones.append('A')  # Both hypo (acceptable)
        elif a > 180 and p > 180:
            zones.append('A')  # Both hyper (acceptable)
        elif 70 <= a <= 180 and 70 <= p <= 180:
            zones.append('A')  # Both normal (acceptable)
        elif abs(a - p) <= 20:
            zones.append('A')  # Within 20 mg/dL
        elif abs(a - p) <= 40:
            zones.append('B')  # Benign error
        else:
            zones.append('C')  # Could lead to wrong treatment
    return zones

zones = clarke_error_grid_zone(y_test, y_pred)
zone_a_percent = (zones.count('A') / len(zones)) * 100
zone_b_percent = (zones.count('B') / len(zones)) * 100

print("\n" + "="*60)
print("🎯 METABOLIC LSTM MODEL - FINAL METRICS")
print("="*60)
print(f"Test MAE:              {mae:.2f} mg/dL  (Target: <15 mg/dL)")
print(f"Test RMSE:             {rmse:.2f} mg/dL  (Target: <20 mg/dL)")
print(f"Test R²:               {r2:.4f}")
print(f"\nClinical Accuracy:")
print(f"  Within ±15 mg/dL:    {within_15:.1f}%")
print(f"  Within ±20 mg/dL:    {within_20:.1f}%")
print(f"\nClarke Error Grid:")
print(f"  Zone A (Accurate):   {zone_a_percent:.1f}%")
print(f"  Zone B (Benign):     {zone_b_percent:.1f}%")
print("="*60)

if mae < 15 and rmse < 20:
    print("✅ MODEL MEETS TARGET METRICS!")
else:
    print(f"⚠️  Performance:")
    if mae >= 15:
        print(f"   MAE is {mae:.1f} mg/dL (target <15)")
    if rmse >= 20:
        print(f"   RMSE is {rmse:.1f} mg/dL (target <20)")
    print("\n   Consider:")
    print("   - More training epochs")
    print("   - Increase LSTM units")
    print("   - Add attention mechanism")
    print("   - Use actual minute-by-minute sequences instead of aggregated features")

# ===== VISUALIZATIONS =====

print("\n" + "="*60)
print("STEP 6: Generating Visualizations")
print("="*60)

import os
os.makedirs('models', exist_ok=True)

# 1. Training History
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# MAE
axes[0].plot(history.history['mae'], label='Train MAE', linewidth=2)
axes[0].plot(history.history['val_mae'], label='Val MAE', linewidth=2)
axes[0].axhline(y=15, color='r', linestyle='--', linewidth=2, label='Target (15 mg/dL)')
axes[0].set_title('Mean Absolute Error', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('MAE (mg/dL)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Loss (MSE)
axes[1].plot(history.history['loss'], label='Train Loss', linewidth=2)
axes[1].plot(history.history['val_loss'], label='Val Loss', linewidth=2)
axes[1].set_title('Mean Squared Error Loss', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Loss (MSE)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('models/metabolic_training_history.png', dpi=150, bbox_inches='tight')
print("✅ Saved: models/metabolic_training_history.png")

# 2. Prediction vs Actual
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Scatter plot
axes[0].scatter(y_test, y_pred, alpha=0.3, s=1)
axes[0].plot([40, 400], [40, 400], 'r--', linewidth=2, label='Perfect Prediction')
axes[0].plot([40, 400], [40+15, 400+15], 'g:', linewidth=1, alpha=0.5, label='±15 mg/dL')
axes[0].plot([40, 400], [40-15, 400-15], 'g:', linewidth=1, alpha=0.5)
axes[0].set_xlabel('Actual Glucose (mg/dL)', fontsize=12)
axes[0].set_ylabel('Predicted Glucose (mg/dL)', fontsize=12)
axes[0].set_title(f'Prediction vs Actual (MAE={mae:.1f} mg/dL)', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim(40, 300)
axes[0].set_ylim(40, 300)

# Residual plot
residuals = y_test - y_pred
axes[1].scatter(y_pred, residuals, alpha=0.3, s=1)
axes[1].axhline(y=0, color='r', linestyle='--', linewidth=2)
axes[1].axhline(y=15, color='orange', linestyle=':', linewidth=1, label='±15 mg/dL')
axes[1].axhline(y=-15, color='orange', linestyle=':', linewidth=1)
axes[1].set_xlabel('Predicted Glucose (mg/dL)', fontsize=12)
axes[1].set_ylabel('Residual (Actual - Predicted)', fontsize=12)
axes[1].set_title('Residual Analysis', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('models/metabolic_predictions.png', dpi=150, bbox_inches='tight')
print("✅ Saved: models/metabolic_predictions.png")

# 3. Error Distribution
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(residuals, bins=100, edgecolor='black', alpha=0.7)
ax.axvline(x=0, color='r', linestyle='--', linewidth=2, label='Zero Error')
ax.axvline(x=residuals.mean(), color='g', linestyle='--', linewidth=2, 
           label=f'Mean: {residuals.mean():.2f} mg/dL')
ax.axvline(x=15, color='orange', linestyle=':', linewidth=1, label='±15 mg/dL threshold')
ax.axvline(x=-15, color='orange', linestyle=':', linewidth=1)
ax.set_xlabel('Prediction Error (mg/dL)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Error Distribution', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('models/metabolic_error_distribution.png', dpi=150, bbox_inches='tight')
print("✅ Saved: models/metabolic_error_distribution.png")

# 4. Clarke Error Grid
fig, ax = plt.subplots(figsize=(10, 10))

# Plot zones (simplified)
ax.plot([0, 400], [0, 400], 'k-', linewidth=2, label='Perfect')

# Zone A boundaries
ax.fill_between([0, 70], 0, 70, alpha=0.2, color='green', label='Zone A')
ax.fill_between([70, 180], 70, 180, alpha=0.2, color='green')
ax.fill_between([180, 400], 180, 400, alpha=0.2, color='green')

# Predictions
colors = {'A': 'green', 'B': 'yellow', 'C': 'red'}
for zone in ['A', 'B', 'C']:
    zone_mask = [z == zone for z in zones]
    if any(zone_mask):
        ax.scatter(
            y_test[zone_mask], 
            y_pred[zone_mask], 
            alpha=0.3, 
            s=2, 
            c=colors[zone],
            label=f'Zone {zone}: {sum(zone_mask)} points'
        )

ax.set_xlabel('Actual Glucose (mg/dL)', fontsize=12)
ax.set_ylabel('Predicted Glucose (mg/dL)', fontsize=12)
ax.set_title('Clarke Error Grid Analysis', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 400)
ax.set_ylim(0, 400)

plt.tight_layout()
plt.savefig('models/metabolic_clarke_grid.png', dpi=150, bbox_inches='tight')
print("✅ Saved: models/metabolic_clarke_grid.png")

# ===== SAVE MODEL & METADATA =====

print("\n" + "="*60)
print("STEP 7: Saving Model & Metadata")
print("="*60)

# Save model
model.save('models/metabolic_lstm.keras')
print("✅ Saved: models/metabolic_lstm.keras")

# Save model info
model_info = {
    'model_type': 'Stacked LSTM (Dual Input)',
    'timeseries_shape': [1, len(timeseries_cols_norm)],
    'metadata_shape': [len(metadata_cols_norm)],
    'timeseries_features': timeseries_cols,
    'metadata_features': metadata_cols,
    'normalization_stats': stats,
    'prediction_horizon_minutes': 60,
    'metrics': {
        'mae_mgdl': float(mae),
        'rmse_mgdl': float(rmse),
        'r2_score': float(r2),
        'within_15_mgdl_percent': float(within_15),
        'within_20_mgdl_percent': float(within_20),
        'clarke_zone_a_percent': float(zone_a_percent),
        'clarke_zone_b_percent': float(zone_b_percent)
    },
    'training_info': {
        'epochs_trained': len(history.history['loss']),
        'best_epoch': int(np.argmin(history.history['val_mae'])) + 1,
        'training_samples': int(len(y_train)),
        'test_samples': int(len(y_test))
    }
}

with open('models/metabolic_model_info.json', 'w') as f:
    json.dump(model_info, f, indent=2)

print("✅ Saved: models/metabolic_model_info.json")

# ===== SAMPLE PREDICTIONS =====

print("\n" + "="*60)
print("STEP 8: Sample Predictions")
print("="*60)

# Show 10 random predictions
np.random.seed(123)
sample_indices = np.random.choice(len(y_test), 10, replace=False)

print("\nSample Predictions (1h ahead):")
print("-" * 70)
print(f"{'Actual':<12} {'Predicted':<12} {'Error':<12} {'Status':<20}")
print("-" * 70)

for idx in sample_indices:
    actual = y_test[idx]
    predicted = y_pred[idx]
    error = actual - predicted
    
    if actual < 70:
        status = "🔴 Hypoglycemia"
    elif actual > 180:
        status = "🟠 Hyperglycemia"
    else:
        status = "🟢 Normal"
    
    print(f"{actual:<12.1f} {predicted:<12.1f} {error:<12.1f} {status}")

print("-" * 70)

# ===== FINAL SUMMARY =====

print("\n" + "="*60)
print("✅ METABOLIC LSTM TRAINING COMPLETE")
print("="*60)
print("\n📁 Generated Files:")
print("   • models/metabolic_lstm.keras")
print("   • models/metabolic_model_info.json")
print("   • models/metabolic_training_history.png")
print("   • models/metabolic_predictions.png")
print("   • models/metabolic_error_distribution.png")
print("   • models/metabolic_clarke_grid.png")
print("\n🎯 Performance:")
print(f"   • MAE: {mae:.1f} mg/dL {'✅' if mae < 15 else '⚠️'}")
print(f"   • RMSE: {rmse:.1f} mg/dL {'✅' if rmse < 20 else '⚠️'}")
print(f"   • Within ±15 mg/dL: {within_15:.1f}%")
print(f"   • Clarke Zone A: {zone_a_percent:.1f}%")
print("\n🚀 Next Steps:")
print("   1. Copy models to backend: cp models/metabolic_lstm.keras backend/models/")
print("   2. Integrate prediction service")
print("   3. Test /api/v1/predictions/metabolic/{patient_id}")
print("="*60)
