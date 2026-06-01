import json

cells = []

# ── CELL 0: Markdown title ────────────────────────────────────────────────────
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# Battery RUL PINN-LSTM — Smart TwinPac Chapter 4 LE-06\n",
        "\n",
        "**Physics Model:** Shepherd Discharge Equation (Chapter 5, Eq 1.1)\n",
        "\n",
        "```\n",
        "V(t) = E0 - R·i - K·(Q/(Q-q))·q + A·exp(-B·q)\n",
        "```\n",
        "\n",
        "## COLAB INSTRUCTIONS:\n",
        "1. Enable GPU: **Runtime → Change runtime type → T4 GPU**\n",
        "2. Run Cell 1 to mount Google Drive\n",
        "3. Upload `battery_cycle_level_dataset_CLEAN_FINAL.csv` to Google Drive folder:\n",
        "   `MyDrive/TwinPacemaker/NASA Battery Dataset/`\n",
        "4. **Runtime → Run all**\n",
        "5. Models saved to: `MyDrive/TwinPacemaker/models/`\n"
    ]
})

# ── CELL 1: Imports + GPU check ───────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import numpy as np\n",
        "import pandas as pd\n",
        "import tensorflow as tf\n",
        "from tensorflow import keras\n",
        "from tensorflow.keras import layers\n",
        "from sklearn.preprocessing import MinMaxScaler\n",
        "from sklearn.model_selection import train_test_split\n",
        "from sklearn.metrics import r2_score\n",
        "import matplotlib.pyplot as plt\n",
        "import json, os\n",
        "\n",
        "SEED = 42\n",
        "np.random.seed(SEED)\n",
        "tf.random.set_seed(SEED)\n",
        "\n",
        "print('='*60)\n",
        "print('BATTERY RUL PINN-LSTM — Smart TwinPac Chapter 4 LE-06')\n",
        "print(f'TensorFlow: {tf.__version__}')\n",
        "gpus = tf.config.list_physical_devices('GPU')\n",
        "print(f'GPU: {gpus}')\n",
        "if not gpus:\n",
        "    print('⚠️  NO GPU! Go to Runtime → Change runtime type → T4 GPU')\n",
        "print('='*60)\n"
    ]
})

# ── CELL 2: Mount Google Drive + Load Data ────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "from google.colab import drive\n",
        "drive.mount('/content/drive')\n",
        "\n",
        "CSV_PATH = '/content/drive/MyDrive/TwinPacemaker/NASA Battery Dataset/battery_cycle_level_dataset_CLEAN_FINAL.csv'\n",
        "MODELS_DIR = '/content/drive/MyDrive/TwinPacemaker/models'\n",
        "os.makedirs(MODELS_DIR, exist_ok=True)\n",
        "\n",
        "df = pd.read_csv(CSV_PATH)\n",
        "print(f'Loaded: {CSV_PATH}')\n",
        "print(f'Shape: {df.shape}')\n",
        "print(df.head())\n",
        "print(f'\\nColumns: {list(df.columns)}')\n"
    ]
})

# ── CELL 3: Markdown — Data Prep ──────────────────────────────────────────────
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 🧹 Step 3 — Data Cleaning & Feature Engineering\n",
        "\n",
        "We add `soc` (State of Charge) = capacity / max_capacity, which measures how\n",
        "much energy is left. This is a key physical indicator of battery health.\n"
    ]
})

# ── CELL 4: Data Cleaning ─────────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# ── Drop missing values and sort by battery + cycle ──────────────────────────\n",
        "df = df.dropna()\n",
        "df = df.sort_values(['battery_id', 'cycle']).reset_index(drop=True)\n",
        "\n",
        "# ── Clip temperature to realistic pacemaker range (Chapter 5 §1.2.1) ─────────\n",
        "df['temperature'] = df['temperature'].clip(30, 45)\n",
        "\n",
        "# ── State of Charge: fraction of max capacity remaining ──────────────────────\n",
        "# Physical meaning: SOC=1.0 = full battery, SOC=0.0 = dead battery\n",
        "df['soc'] = df['capacity'] / (df['capacity'].max() + 1e-6)\n",
        "\n",
        "FEATURES = ['voltage', 'temperature', 'capacity', 'soc']\n",
        "TARGET   = 'rul'\n",
        "\n",
        "print(f'Features: {FEATURES}')\n",
        "print(f'Target:   {TARGET} (cycles remaining)')\n",
        "print(f'\\nRUL range: {df[TARGET].min()} – {df[TARGET].max()} cycles')\n",
        "print(f'Batteries: {df[\"battery_id\"].nunique()}')\n",
        "print(f'Total rows: {len(df)}')\n"
    ]
})

# ── CELL 5: Markdown — Normalization ─────────────────────────────────────────
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 📊 Step 4 — Normalization (CRITICAL)\n",
        "\n",
        "Neural networks learn much better when all numbers are in the range **0 → 1**.\n",
        "\n",
        "- **Features** → scaled with MinMaxScaler (each column independently mapped to 0–1)\n",
        "- **RUL target** → divided by `RUL_MAX` so the network outputs a number between 0 and 1\n",
        "  - At the end, we multiply back by `RUL_MAX` to get the real cycle count\n",
        "\n",
        "This is **Bug #2** that broke the original model — the original output raw days (0–2520)\n",
        "instead of normalizing them.\n"
    ]
})

# ── CELL 6: Normalization ─────────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "feature_scaler = MinMaxScaler()\n",
        "df[FEATURES] = feature_scaler.fit_transform(df[FEATURES])\n",
        "\n",
        "# Normalize RUL to 0–1 range (CRITICAL FIX)\n",
        "RUL_MAX = df[TARGET].max()\n",
        "df[TARGET] = df[TARGET] / RUL_MAX\n",
        "\n",
        "print(f'RUL_MAX (for inverse transform later): {RUL_MAX} cycles')\n",
        "print(f'Normalized RUL range: {df[TARGET].min():.4f} – {df[TARGET].max():.4f}')\n"
    ]
})

# ── CELL 7: Markdown — Sliding Window ────────────────────────────────────────
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 🔁 Step 5 — Sliding Window Sequences (CRITICAL)\n",
        "\n",
        "An LSTM needs a **sequence** of timesteps, not a single snapshot.\n",
        "\n",
        "We use `SEQ_LEN = 30` meaning: look at the last 30 cycles to predict the RUL at cycle 31.\n",
        "\n",
        "```\n",
        "Cycles 1–30  → predict RUL at cycle 31\n",
        "Cycles 2–31  → predict RUL at cycle 32\n",
        "...\n",
        "```\n",
        "\n",
        "This is **Bug #1** in the original model — it used `reshape(-1, 1, features)` giving\n",
        "only 1 timestep. Fixed here by creating proper 30-step windows.\n"
    ]
})

# ── CELL 8: Sliding Window ────────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "SEQ_LEN = 30   # Look at 30 past cycles to predict the next RUL\n",
        "\n",
        "X, y = [], []\n",
        "\n",
        "for bid, g in df.groupby('battery_id'):\n",
        "    g = g.sort_values('cycle')\n",
        "    x_data = g[FEATURES].values      # shape (n_cycles, 4)\n",
        "    y_data = g[TARGET].values        # shape (n_cycles,)\n",
        "\n",
        "    for i in range(len(g) - SEQ_LEN):\n",
        "        X.append(x_data[i:i + SEQ_LEN])   # window of 30 cycles\n",
        "        y.append(y_data[i + SEQ_LEN])     # RUL at the next cycle\n",
        "\n",
        "X = np.array(X, dtype=np.float32)   # shape: (N_samples, 30, 4)\n",
        "y = np.array(y, dtype=np.float32)   # shape: (N_samples,)\n",
        "\n",
        "print(f'X shape: {X.shape}  → (samples, timesteps=30, features=4)')\n",
        "print(f'y shape: {y.shape}')\n",
        "print(f'Total sequences: {len(X)}')\n"
    ]
})

# ── CELL 9: Train/Test split ──────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "X_train, X_test, y_train, y_test = train_test_split(\n",
        "    X, y, test_size=0.2, random_state=42\n",
        ")\n",
        "print(f'Train: {X_train.shape[0]} samples')\n",
        "print(f'Test:  {X_test.shape[0]} samples')\n"
    ]
})

# ── CELL 10: Markdown — PINN Architecture ─────────────────────────────────────
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 🧠 Step 6 — PINN-LSTM Model\n",
        "\n",
        "Standard LSTM learns patterns from data. We add a **Physics Loss** based on the\n",
        "**Shepherd Battery Discharge Equation** (Chapter 5, Eq 1.1):\n",
        "\n",
        "```\n",
        "V(t) = E₀ − R·i − K·(Q/(Q−q))·q + A·exp(−B·q)\n",
        "```\n",
        "\n",
        "The model is:\n",
        "```\n",
        "Input (30 cycles × 4 features)\n",
        "  → LSTM(128) + LayerNorm + Dropout(0.2)\n",
        "  → LSTM(64)\n",
        "  → LSTM(32)\n",
        "  → Dense(64, relu)\n",
        "  → Dense(32, relu)\n",
        "  → Dense(1, sigmoid)   ← output between 0 and 1\n",
        "  × RUL_MAX             ← convert back to cycles\n",
        "```\n",
        "\n",
        "**Loss = data_loss + 0.1 × physics_loss + 0.05 × monotonic_loss**\n",
        "- `data_loss`: (predicted − actual)² — standard MSE\n",
        "- `physics_loss`: forces predictions to respect battery degradation physics\n",
        "- `monotonic_loss`: penalizes if RUL goes UP (it should only go DOWN)\n"
    ]
})

# ── CELL 11: Model Definition ─────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# ── PINN-LSTM Model ───────────────────────────────────────────────────────────\n",
        "inputs = keras.Input(shape=(SEQ_LEN, len(FEATURES)), name='battery_sequence')\n",
        "\n",
        "x = layers.LSTM(128, return_sequences=True)(inputs)\n",
        "x = layers.LayerNormalization()(x)\n",
        "x = layers.Dropout(0.2)(x)\n",
        "\n",
        "x = layers.LSTM(64, return_sequences=True)(x)\n",
        "x = layers.LSTM(32)(x)\n",
        "\n",
        "x = layers.Dense(64, activation='relu')(x)\n",
        "x = layers.Dense(32, activation='relu')(x)\n",
        "\n",
        "rul_output = layers.Dense(1, activation='sigmoid', name='rul_output')(x)\n",
        "\n",
        "model = keras.Model(inputs, rul_output)\n",
        "model.summary()\n"
    ]
})

# ── CELL 12: Physics Loss ─────────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# ── Physics-Informed Loss (Shepherd degradation concept) ─────────────────────\n",
        "#\n",
        "# Full Shepherd: V(t) = E0 - R*i - K*(Q/(Q-q))*q + A*exp(-B*q)\n",
        "#\n",
        "# Here we use a simplified physics penalty:\n",
        "#   degradation = capacity / (voltage + eps)\n",
        "#   As the battery ages: capacity ↓, voltage ↓ → degradation ratio changes\n",
        "#   We want predicted RUL to correlate with this degradation ratio.\n",
        "#\n",
        "# The PINN forces the LSTM to be consistent with physical battery behavior.\n",
        "\n",
        "def physics_loss(x_batch, y_pred):\n",
        "    # x_batch shape: (batch, 30, 4) — last timestep is x[:, -1, :]\n",
        "    voltage  = x_batch[:, -1, 0]   # normalized voltage\n",
        "    capacity = x_batch[:, -1, 2]   # normalized capacity\n",
        "\n",
        "    voltage  = tf.clip_by_value(voltage, 0.1, 1.0)\n",
        "    capacity = tf.clip_by_value(capacity, 0.0, 1.0)\n",
        "\n",
        "    # Physical degradation signal: as battery ages, this ratio changes\n",
        "    # (Simplified Shepherd: higher capacity/voltage = more life remaining)\n",
        "    degradation = capacity / (voltage + 1e-3)\n",
        "    degradation = tf.clip_by_value(degradation, 0.0, 5.0)\n",
        "\n",
        "    # Penalize predictions that don't match this physical signal\n",
        "    return tf.reduce_mean(tf.square(y_pred - tf.stop_gradient(degradation)))\n",
        "\n",
        "print('Physics loss function defined ✓')\n",
        "print()\n",
        "print('Physics concept:')\n",
        "print('  capacity / voltage → battery degradation ratio')\n",
        "print('  New battery:  ~1.86Ah / ~3.7V ≈ 0.50')\n",
        "print('  Dying battery: ~1.40Ah / ~2.9V ≈ 0.48')\n",
        "print('  The LSTM must agree with this physical trend.')\n"
    ]
})

# ── CELL 13: Custom Training Step ─────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "optimizer = tf.keras.optimizers.Adam(1e-3)\n",
        "\n",
        "@tf.function\n",
        "def train_step(x, y):\n",
        "    y = tf.cast(y, tf.float32)\n",
        "    with tf.GradientTape() as tape:\n",
        "        y_pred = tf.squeeze(model(x, training=True))\n",
        "\n",
        "        # 1. Data loss: how far prediction is from ground truth\n",
        "        data_loss = tf.reduce_mean(tf.square(y - y_pred))\n",
        "\n",
        "        # 2. Physics loss: must respect Shepherd degradation signal\n",
        "        phys_loss = physics_loss(x, y_pred)\n",
        "\n",
        "        # 3. Monotonicity: RUL should only go DOWN, never UP\n",
        "        monotonic = tf.reduce_mean(tf.maximum(0.0, y_pred[1:] - y_pred[:-1]))\n",
        "\n",
        "        # Combined PINN loss (Chapter 4 Table 4.10 weights)\n",
        "        total_loss = data_loss + 0.1 * phys_loss + 0.05 * monotonic\n",
        "\n",
        "    grads = tape.gradient(total_loss, model.trainable_variables)\n",
        "    optimizer.apply_gradients(zip(grads, model.trainable_variables))\n",
        "    return total_loss\n",
        "\n",
        "print('Custom PINN train step defined ✓')\n"
    ]
})

# ── CELL 14: Training Loop ─────────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "BATCH  = 32\n",
        "EPOCHS = 50\n",
        "\n",
        "train_ds = tf.data.Dataset.from_tensor_slices((X_train, y_train))\n",
        "train_ds = train_ds.shuffle(1000).batch(BATCH)\n",
        "\n",
        "print(f'Training for {EPOCHS} epochs, batch size {BATCH}...')\n",
        "print('='*50)\n",
        "\n",
        "for epoch in range(EPOCHS):\n",
        "    losses = []\n",
        "    for xb, yb in train_ds:\n",
        "        loss = train_step(xb, yb)\n",
        "        losses.append(loss.numpy())\n",
        "    if (epoch + 1) % 5 == 0:\n",
        "        print(f'Epoch {epoch+1:3d}/{EPOCHS}: Loss = {np.mean(losses):.4f}')\n",
        "\n",
        "print('\\nTraining complete ✓')\n"
    ]
})

# ── CELL 15: Markdown — Evaluation ───────────────────────────────────────────
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 📊 Step 8 — Evaluation\n",
        "\n",
        "We convert predictions back from 0–1 range to real cycle counts\n",
        "by multiplying by `RUL_MAX`.\n",
        "\n",
        "| Metric | Meaning | Target |\n",
        "|--------|---------|--------|\n",
        "| MAE | Average error in cycles | < 15 cycles |\n",
        "| RMSE | Penalizes large errors more | as low as possible |\n",
        "| R² | 1.0 = perfect, 0 = random | > 0.80 |\n"
    ]
})

# ── CELL 16: Evaluation ───────────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Predict and convert back to real cycle counts\n",
        "pred = model.predict(X_test).squeeze()\n",
        "pred_cycles = pred * RUL_MAX\n",
        "true_cycles = y_test * RUL_MAX\n",
        "\n",
        "mae  = np.mean(np.abs(true_cycles - pred_cycles))\n",
        "rmse = np.sqrt(np.mean((true_cycles - pred_cycles)**2))\n",
        "r2   = r2_score(true_cycles, pred_cycles)\n",
        "\n",
        "print('='*55)\n",
        "print('BATTERY PINN-LSTM — FINAL RESULTS')\n",
        "print('='*55)\n",
        "print(f'MAE:  {mae:.2f} cycles  (target: < 15 cycles)')\n",
        "print(f'RMSE: {rmse:.2f} cycles')\n",
        "print(f'R²:   {r2:.4f}  (target: > 0.80)')\n",
        "print('='*55)\n",
        "\n",
        "# Compare with simple baseline (aaa.ipynb)\n",
        "print()\n",
        "print('Comparison with simple LSTM (aaa.ipynb):')\n",
        "print(f'  Simple LSTM:  MAE=11.28 cycles, R²=0.82')\n",
        "print(f'  PINN-LSTM:    MAE={mae:.2f} cycles, R²={r2:.4f}')\n"
    ]
})

# ── CELL 17: Plot ─────────────────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "plt.figure(figsize=(10, 5))\n",
        "plt.scatter(true_cycles[:200], pred_cycles[:200], alpha=0.5, s=20)\n",
        "plt.plot([0, RUL_MAX], [0, RUL_MAX], 'r--', label='Perfect prediction')\n",
        "plt.xlabel('True RUL (cycles)')\n",
        "plt.ylabel('Predicted RUL (cycles)')\n",
        "plt.title(f'PINN-LSTM Battery RUL — MAE={mae:.1f} cycles, R²={r2:.2f}')\n",
        "plt.legend()\n",
        "plt.tight_layout()\n",
        "plt.savefig(f'{MODELS_DIR}/battery_pinn_results.png', dpi=150)\n",
        "plt.show()\n",
        "print('Plot saved to Google Drive ✓')\n"
    ]
})

# ── CELL 18: Save Model ───────────────────────────────────────────────────────
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Save model to Google Drive (persists across sessions!)\n",
        "model_path = f'{MODELS_DIR}/battery_pinn_lstm.keras'\n",
        "model.save(model_path)\n",
        "print(f'Model saved: {model_path} ✓')\n",
        "\n",
        "# Save metadata for the app to use\n",
        "info = {\n",
        "    'model_type': 'PINN-LSTM',\n",
        "    'chapter_ref': 'Chapter 4 LE-06 / Chapter 5 §1.4.2',\n",
        "    'rul_max_cycles': int(RUL_MAX),\n",
        "    'seq_len': SEQ_LEN,\n",
        "    'features': FEATURES,\n",
        "    'metrics': {\n",
        "        'mae_cycles': round(float(mae), 2),\n",
        "        'rmse_cycles': round(float(rmse), 2),\n",
        "        'r2': round(float(r2), 4)\n",
        "    },\n",
        "    'physics': 'Shepherd discharge equation: V(t) = E0 - R*i - K*(Q/(Q-q))*q + A*exp(-B*q)',\n",
        "    'loss_weights': {'data': 1.0, 'physics': 0.1, 'monotonic': 0.05},\n",
        "    'scaler_min': feature_scaler.data_min_.tolist(),\n",
        "    'scaler_max': feature_scaler.data_max_.tolist()\n",
        "}\n",
        "\n",
        "info_path = f'{MODELS_DIR}/battery_rul_model_info.json'\n",
        "with open(info_path, 'w') as f:\n",
        "    json.dump(info, f, indent=2)\n",
        "print(f'Model info saved: {info_path} ✓')\n",
        "print()\n",
        "print('All outputs saved to Google Drive — they will NOT disappear!')\n"
    ]
})

# ── Write notebook ─────────────────────────────────────────────────────────────
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
        "colab": {"provenance": []}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

filepath = r'D:\Vibe Coding\TwinPacemaker\notebooks\01_battery_training.ipynb'
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"Successfully rebuilt {filepath}")
