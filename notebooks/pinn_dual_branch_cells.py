"""
=============================================================================
DUAL-BRANCH PINN-LSTM — FIXED ARCHITECTURE
For: D:\Vibe Coding\TwinPacemaker\notebooks\01_battery_training.ipynb
=============================================================================

Replace the MODEL BUILD cell (Step 6) and TRAINING cell (Step 7–10)
with the cells below.

Architecture implemented:
 
  Input (30 cycles × 4 features)
         │
    ┌────┴──────────────────────┐
    │                           │
┌───▼──────────────┐   ┌────────▼───────────────────┐
│ LSTM (128)       │   │ ShepherdPhysicsLayer        │
│ LayerNorm        │   │ (learns E0, R, K, A, B)     │
│ Dropout(0.2)     │   │ → computes V from equation  │
│ LSTM (64)        │   │ → outputs physics residuals │
│ LSTM (32)        │   └────────┬───────────────────-┘
│ Dense(32, relu)  │            │
└───┬──────────────┘            │
    │                           │
    └──────────┬────────────────┘
               │ Concatenate (32+16=48)
     ┌─────────▼──────────┐
     │   Dense (16, relu) │
     └─────────┬──────────┘
               │
     ┌─────────▼──────────┐
     │  Dense(1, sigmoid) │ → RUL (0→1), then × RUL_MAX = cycles
     └────────────────────┘

=============================================================================
"""

# ============================================================
# CELL 1: IMPORTS (add to existing import cell)
# ============================================================
CELL_1_IMPORTS = """
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import json, os

SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)

print('='*60)
print('BATTERY RUL PINN-LSTM — Dual-Branch Architecture')
print(f'TensorFlow: {tf.__version__}')
gpus = tf.config.list_physical_devices('GPU')
print(f'GPU: {gpus}')
if not gpus:
    print('⚠️  NO GPU! Go to Runtime → Change runtime type → T4 GPU')
print('='*60)
"""

# ============================================================
# CELL 2: SHEPHERD PHYSICS LAYER (NEW — add before model build)
# ============================================================
CELL_2_PHYSICS_LAYER = """
# ── Shepherd Physics Layer (Dual-Branch PINN) ─────────────────────────────
# 
# Shepherd Discharge Equation (Chapter 5, Eq 1.1 of your thesis):
#   V(t) = E0 - R·i - K·(Q/(Q-q))·q + A·exp(-B·q)
#
# Parameters learned from data:
#   E0 = open-circuit voltage
#   R  = internal resistance (grows with aging → battery degrades)
#   K  = polarization coefficient
#   A  = exponential zone amplitude
#   B  = exponential time constant
#
# Current i is constant for pacemaker (10 µA) → absorbed into R·i term
# q  ≈ normalized capacity (how much charge was extracted)
# Q  = 1.0 (normalized full capacity)

class ShepherdPhysicsLayer(keras.layers.Layer):
    \"\"\"
    Learnable Shepherd battery discharge model.
    Takes the full 30-cycle sequence as input.
    Uses the LAST timestep for physics computation.
    Outputs 3 physics features: [V_shepherd, physics_residual, degradation_signal]
    \"\"\"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def build(self, input_shape):
        # Learnable physics parameters
        self.E0 = self.add_weight(
            name='E0', shape=(), dtype=tf.float32,
            initializer=tf.constant_initializer(1.0),  # ~3.7V normalized
            trainable=True
        )
        self.R = self.add_weight(
            name='R', shape=(), dtype=tf.float32,
            initializer=tf.constant_initializer(0.05),  # small internal resistance
            trainable=True
        )
        self.K = self.add_weight(
            name='K', shape=(), dtype=tf.float32,
            initializer=tf.constant_initializer(0.1),
            trainable=True
        )
        self.A = self.add_weight(
            name='A', shape=(), dtype=tf.float32,
            initializer=tf.constant_initializer(0.3),
            trainable=True
        )
        self.B = self.add_weight(
            name='B', shape=(), dtype=tf.float32,
            initializer=tf.constant_initializer(3.0),
            trainable=True
        )
        super().build(input_shape)
    
    def call(self, inputs):
        # inputs shape: (batch, 30, 4)
        # features order: [voltage, temperature, capacity, soc]
        
        # Use LAST timestep for physics (most recent battery state)
        voltage  = inputs[:, -1, 0]   # normalized voltage   shape: (batch,)
        capacity = inputs[:, -1, 2]   # normalized capacity  shape: (batch,)
        
        # In Shepherd model:
        # q = charge extracted = (1 - normalized_capacity) * Q_max
        # normalized: q ≈ 1.0 - capacity  (0 = full, 1 = empty)
        # Q = 1.0 (normalized full capacity)
        Q   = tf.ones_like(capacity)          # normalized full capacity = 1.0
        q   = tf.clip_by_value(1.0 - capacity, 0.0, 0.99)  # extracted charge
        eps = 1e-6
        
        # ── Shepherd Equation (simplified: R·i → R·i absorbed into R term) ──
        # V_shepherd = E0 - R - K*(Q/(Q-q))*q + A*exp(-B*q)
        V_shepherd = (
            self.E0
            - self.R
            - self.K * (Q / (Q - q + eps)) * q
            + self.A * tf.exp(-self.B * q)
        )
        V_shepherd = tf.clip_by_value(V_shepherd, 0.0, 2.0)
        
        # ── Physics Residual: measured V vs. Shepherd-predicted V ──────────
        # A large residual = battery deviating from ideal = aging detected
        physics_residual = voltage - V_shepherd
        
        # ── Degradation Signal: absolute deviation ──────────────────────────
        degradation_signal = tf.abs(physics_residual)
        
        # Stack into (batch, 3) feature vector
        return tf.stack([V_shepherd, physics_residual, degradation_signal], axis=-1)
    
    def get_learned_params(self):
        \"\"\"Print the learned physical parameters after training.\"\"\"
        print(f'Learned Shepherd Parameters:')
        print(f'  E0 (open-circuit voltage): {self.E0.numpy():.4f} (normalized)')
        print(f'  R  (internal resistance):  {self.R.numpy():.4f}')
        print(f'  K  (polarization coeff.):  {self.K.numpy():.4f}')
        print(f'  A  (exp. amplitude):        {self.A.numpy():.4f}')
        print(f'  B  (exp. time constant):    {self.B.numpy():.4f}')
    
    def get_config(self):
        return super().get_config()


print('✅ ShepherdPhysicsLayer defined')
print()
print('Physical parameters to be learned:')
print('  E0 = open-circuit voltage (≈3.7V normalized)')
print('  R  = internal resistance (grows as battery ages)')
print('  K  = polarization coefficient')
print('  A  = exponential zone amplitude')
print('  B  = exponential time constant')
"""

# ============================================================
# CELL 3: DUAL-BRANCH MODEL BUILD (replaces old model cell)
# ============================================================
CELL_3_MODEL = """
# ── Dual-Branch PINN-LSTM Model ───────────────────────────────────────────
#
# Branch 1 (LSTM): Learns temporal degradation PATTERNS from 30 cycles
# Branch 2 (Physics): Learns Shepherd equation PARAMETERS from physics
# → Both branches merged → Final RUL prediction

# ── Input ─────────────────────────────────────────────────────────────────
inputs = keras.Input(shape=(SEQ_LEN, len(FEATURES)), name='battery_sequence')

# ── Branch 1: LSTM (Temporal Pattern Learning) ────────────────────────────
x1 = layers.LSTM(128, return_sequences=True, name='lstm_1')(inputs)
x1 = layers.LayerNormalization(name='layer_norm')(x1)
x1 = layers.Dropout(0.2, name='dropout')(x1)
x1 = layers.LSTM(64, return_sequences=True, name='lstm_2')(x1)
x1 = layers.LSTM(32, name='lstm_3')(x1)              # (batch, 32)
x1 = layers.Dense(32, activation='relu', name='lstm_dense')(x1)   # (batch, 32)

# ── Branch 2: Shepherd Physics Layer ──────────────────────────────────────
x2 = ShepherdPhysicsLayer(name='shepherd_physics')(inputs)  # (batch, 3)
x2 = layers.Dense(16, activation='relu', name='physics_dense_1')(x2)  # (batch, 16)
x2 = layers.Dense(16, activation='relu', name='physics_dense_2')(x2)  # (batch, 16)

# ── Merge: Concatenate both branches ─────────────────────────────────────
x = layers.Concatenate(name='merge')([x1, x2])       # (batch, 32+16=48)

# ── Final Prediction ──────────────────────────────────────────────────────
x = layers.Dense(16, activation='relu', name='final_dense')(x)
rul_output = layers.Dense(1, activation='sigmoid', name='rul_output')(x)

# ── Build model ───────────────────────────────────────────────────────────
model = keras.Model(inputs, rul_output, name='PINN_LSTM_DualBranch')
model.summary()

print()
print('Architecture:')
print('  Branch 1 (LSTM):    Learns TEMPORAL PATTERNS across 30 cycles')
print('  Branch 2 (Physics): Learns E0, R, K, A, B from Shepherd equation')
print('  Merge → Dense(16) → Dense(1, sigmoid) → RUL')
"""

# ============================================================
# CELL 4: PHYSICS LOSS (unchanged from current notebook)
# ============================================================
CELL_4_PHYSICS_LOSS = """
# ── Physics-Informed Loss ─────────────────────────────────────────────────
# 
# NOTE: The ShepherdPhysicsLayer LEARNS the physics parameters.
# This additional loss PENALIZES predictions that deviate from
# the physics signal — double enforcement of physical constraints.

def physics_loss(x_batch, y_pred):
    voltage  = x_batch[:, -1, 0]
    capacity = x_batch[:, -1, 2]
    
    voltage  = tf.clip_by_value(voltage, 0.1, 1.0)
    capacity = tf.clip_by_value(capacity, 0.0, 1.0)
    
    # Physical degradation signal (Shepherd-derived)
    degradation = capacity / (voltage + 1e-3)
    degradation = tf.clip_by_value(degradation, 0.0, 5.0)
    
    return tf.reduce_mean(tf.square(y_pred - tf.stop_gradient(degradation)))

print('✅ Physics loss function defined')
"""

# ============================================================
# CELL 5: TRAINING STEP (unchanged from current notebook)
# ============================================================
CELL_5_TRAIN_STEP = """
optimizer = tf.keras.optimizers.Adam(1e-3)

@tf.function
def train_step(x, y):
    y = tf.cast(y, tf.float32)
    with tf.GradientTape() as tape:
        y_pred = tf.squeeze(model(x, training=True))
        
        # 1. Data loss
        data_loss = tf.reduce_mean(tf.square(y - y_pred))
        
        # 2. Physics loss (Shepherd constraint)
        phys_loss = physics_loss(x, y_pred)
        
        # 3. Monotonicity (RUL can ONLY go DOWN)
        monotonic = tf.reduce_mean(tf.maximum(0.0, y_pred[1:] - y_pred[:-1]))
        
        # Combined PINN loss (Chapter 4 weights)
        total_loss = data_loss + 0.1 * phys_loss + 0.05 * monotonic
    
    grads = tape.gradient(total_loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return total_loss

print('✅ PINN train step defined')
print('Loss = data_loss + 0.1×physics_loss + 0.05×monotonic_loss')
"""

# ============================================================
# CELL 6: TRAINING LOOP (unchanged from current notebook)
# ============================================================
CELL_6_TRAINING = """
BATCH  = 32
EPOCHS = 50

train_ds = tf.data.Dataset.from_tensor_slices((X_train, y_train)).shuffle(1000).batch(BATCH, drop_remainder=True)
val_ds   = tf.data.Dataset.from_tensor_slices((X_test,  y_test)).batch(BATCH, drop_remainder=True)

history = {'loss': [], 'val_loss': []}
print(f'Training for {EPOCHS} epochs with Dual-Branch PINN loss...')

for epoch in range(EPOCHS):
    train_losses = []
    for xb, yb in train_ds:
        loss = train_step(xb, yb)
        train_losses.append(loss.numpy())
    
    epoch_loss = np.mean(train_losses)
    history['loss'].append(epoch_loss)
    
    val_losses = []
    for xb, yb in val_ds:
        y_pred = model(xb, training=False)
        y_pred = tf.reshape(y_pred, [-1])
        yb     = tf.reshape(yb, [-1])
        
        data_loss    = tf.reduce_mean(tf.square(yb - y_pred))
        phys_loss    = physics_loss(xb, y_pred)
        delta_pred   = y_pred[1:] - y_pred[:-1]
        delta_true   = yb[1:]     - yb[:-1]
        invalid_incr = tf.maximum(0.0, delta_pred)
        mask         = tf.cast(delta_true <= 0, tf.float32)
        monotonic    = tf.reduce_mean(invalid_incr * mask)
        total_val    = data_loss + 0.1 * phys_loss + 0.05 * monotonic
        val_losses.append(total_val.numpy())
    
    epoch_val_loss = np.mean(val_losses)
    history['val_loss'].append(epoch_val_loss)
    
    if (epoch + 1) % 5 == 0 or epoch == 0:
        print(f'Epoch {epoch+1:3d}/{EPOCHS}: Train={epoch_loss:.4f} | Val={epoch_val_loss:.4f}')

print('\\n✅ Training complete!')
"""

# ============================================================
# CELL 7: EVALUATION + LEARNED PHYSICS PARAMETERS (NEW)
# ============================================================
CELL_7_EVAL = """
# ── Evaluation ───────────────────────────────────────────────────────────
pred        = model.predict(X_test).squeeze()
pred_cycles = pred * RUL_MAX
true_cycles = y_test * RUL_MAX

mae  = np.mean(np.abs(true_cycles - pred_cycles))
rmse = np.sqrt(np.mean((true_cycles - pred_cycles)**2))
r2   = r2_score(true_cycles, pred_cycles)

print('='*55)
print('DUAL-BRANCH PINN-LSTM — FINAL RESULTS')
print('='*55)
print(f'MAE:  {mae:.2f} cycles  (target: < 15 cycles)')
print(f'RMSE: {rmse:.2f} cycles')
print(f'R²:   {r2:.4f}  (target: > 0.80)')
print('='*55)

# ── Learned Shepherd Parameters ───────────────────────────────────────────
print()
print('='*55)
print('LEARNED PHYSICS PARAMETERS (Shepherd Model)')
print('='*55)
shepherd_layer = model.get_layer('shepherd_physics')
shepherd_layer.get_learned_params()
print()
print('Interpretation:')
print('  E0 → open-circuit voltage of the cell')
print('  R  → internal resistance (higher = more aged battery)')
print('  K  → polarization effect (higher = steeper voltage drop)')
print('  A,B → exponential zone (end-of-discharge behavior)')
"""

# ============================================================
# CELL 8: SAVE MODEL (same as current)
# ============================================================
CELL_8_SAVE = """
# ── Save Model ────────────────────────────────────────────────────────────
model.save(f'{MODELS_DIR}/battery_pinn_lstm_dual.keras')

model_info = {
    'rul_max':       int(RUL_MAX),
    'seq_len':       SEQ_LEN,
    'features':      FEATURES,
    'architecture':  'PINN-LSTM Dual-Branch (LSTM + Shepherd Physics)',
    'shepherd_params': {
        'E0': float(shepherd_layer.E0.numpy()),
        'R':  float(shepherd_layer.R.numpy()),
        'K':  float(shepherd_layer.K.numpy()),
        'A':  float(shepherd_layer.A.numpy()),
        'B':  float(shepherd_layer.B.numpy()),
    },
    'metrics': {
        'mae_cycles':  round(float(mae),  2),
        'rmse_cycles': round(float(rmse), 2),
        'r2':          round(float(r2),   4),
    }
}

with open(f'{MODELS_DIR}/battery_pinn_dual_info.json', 'w') as f:
    json.dump(model_info, f, indent=2)

print('✅ Model saved:', f'{MODELS_DIR}/battery_pinn_lstm_dual.keras')
print('✅ Info  saved:', f'{MODELS_DIR}/battery_pinn_dual_info.json')
print()
print('Model info:')
print(json.dumps(model_info, indent=2))
"""

if __name__ == '__main__':
    print("=" * 60)
    print("DUAL-BRANCH PINN-LSTM CELL CODE")
    print("Copy each CELL_N_ block into your Colab notebook")
    print("=" * 60)
    print()
    for name, code in [
        ("CELL 2 — ShepherdPhysicsLayer", CELL_2_PHYSICS_LAYER),
        ("CELL 3 — Dual-Branch Model",    CELL_3_MODEL),
        ("CELL 4 — Physics Loss",         CELL_4_PHYSICS_LOSS),
        ("CELL 5 — Train Step",           CELL_5_TRAIN_STEP),
        ("CELL 6 — Training Loop",        CELL_6_TRAINING),
        ("CELL 7 — Evaluation",           CELL_7_EVAL),
        ("CELL 8 — Save",                 CELL_8_SAVE),
    ]:
        print(f"\n{'─'*60}")
        print(f"  {name}")
        print(f"{'─'*60}")
        print(code)
