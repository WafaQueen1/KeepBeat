# Battery RUL Models: Full Explanation & Comparison

## 🔋 What Are We Trying to Do?

A **pacemaker battery** (Lithium-CFx, ~1.85 Ah) must last **7 years = 2520 days**.
When the battery is about to die, the pacemaker stops working → the patient dies.

**The Goal:** Given measurements of the battery RIGHT NOW (voltage, temperature, capacity),
predict **how many days remain** before the battery dies. This is called **RUL = Remaining Useful Life**.

The dataset used is the **NASA Battery Dataset** — batteries that were cycled (charged + discharged)
in a lab until they died. Each row = one discharge cycle. Columns: `voltage`, `temperature`, `capacity`, `soh`, `rul`.

---

## 📚 How Both Models See the Data

Both models look at a **window of recent cycles** and ask:
*"Based on the last N cycles of battery behavior, how many cycles/days are left?"*

Think of it like a doctor looking at your last 30 blood test results to predict your health.

```
Cycle 1  [voltage=3.53, temp=32.5, capacity=1.86]  ─┐
Cycle 2  [voltage=3.54, temp=32.6, capacity=1.85]   │
...                                                   ├─► LSTM ─► "167 cycles left"
Cycle 29 [voltage=3.49, temp=33.1, capacity=1.72]   │
Cycle 30 [voltage=3.48, temp=33.2, capacity=1.70]  ─┘
```

---

## 🅰️ Model A — `aaa.ipynb` (The Simple One That Works)

### Architecture

```
Input: 30 cycles × 4 features (voltage, temperature, capacity, soc)
         │
    ┌────▼────────┐
    │  LSTM (128) │ ← learns patterns across 30 timesteps
    │  + LayerNorm│
    │  + Dropout  │
    └────┬────────┘
         │
    ┌────▼────────┐
    │  LSTM (64)  │ ← refines the pattern
    └────┬────────┘
         │
    ┌────▼────────┐
    │  LSTM (32)  │
    └────┬────────┘
         │
    ┌────▼────────┐
    │  Dense (64) │
    └────┬────────┘
         │
    ┌────▼────────┐
    │  Dense (32) │
    └────┬────────┘
         │
    ┌────▼──────────────────┐
    │  Dense(1, sigmoid)    │ ← outputs a number between 0 and 1
    └────┬──────────────────┘
         │
    Output × RUL_MAX = Predicted cycles remaining
```

### Loss Function (How It Learns)

```
Total Loss = data_loss + 0.1 × physics_loss + 0.05 × monotonic_loss
```

- **data_loss** = (predicted - actual)² → standard MSE
- **physics_loss** = forces predictions to match a degradation formula:
  `degradation = capacity / (voltage + 0.001)` → simple formula
- **monotonic_loss** = penalizes if predictions go UP (RUL should always go DOWN)

### Results
| Metric | Value |
|--------|-------|
| MAE    | **11.28 cycles** |
| RMSE   | **15.16 cycles** |
| R²     | **0.82** ✅ |

> **Why does it work?** Proper 30-step temporal windows + simple normalized target (0→1).

---

## 🅱️ Model B — `01_battery_training.ipynb` (The Complex One That Fails)

### What Is PINN?

**PINN = Physics-Informed Neural Network**

A standard neural network learns purely from data. A PINN also forces the network
to obey **known physics equations** during training.

**For batteries**, the physics equation used is the **Shepherd Discharge Model:**

```
V(t) = E₀ − R·i − K·(Q/(Q−q))·q + A·exp(−B·q)
```

| Symbol | Meaning | Value |
|--------|---------|-------|
| V(t)   | Voltage at time t | measured |
| E₀     | Open-circuit voltage | 3.7V |
| R      | Internal resistance (increases with age) | **learned** |
| i      | Current | 10 µA (constant for pacemaker) |
| K      | Polarization coefficient | **learned** |
| Q      | Total battery capacity | 1.85 Ah |
| q      | Discharged capacity so far | Q - capacity_current |
| A      | Exponential zone amplitude | **learned** |
| B      | Exponential time constant | **learned** |

In plain English:
- As the battery ages, `R` (internal resistance) gets bigger → voltage drops faster
- `K` and `A`, `B` describe how the voltage curve bends at the end of life
- The model **learns** these 4 physical parameters from the data

### Architecture (Dual-Branch PINN)

```
Input: (N batteries × 1 timestep × 13 features)  ← BUG: should be 10 timesteps!
         │
    ┌────┴──────────┐
    │               │
┌───▼────┐    ┌────▼────────────────┐
│LSTM(128)│    │ Shepherd Physics   │  ← calculates V using the equation above
│LSTM(64) │    │ Layer (learns R,K, │
│Dense(32)│    │ A, B)              │
└───┬────┘    └────┬────────────────┘
    │               │
    └──────┬────────┘
           │ Concatenate
    ┌──────▼──────┐
    │  Dense (16) │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │  Dense (1)  │ → RUL in DAYS (0–2520 days)
    └─────────────┘
```

### The Two Bugs That Killed Performance

**Bug #1: Timesteps = 1 (The Fatal Bug)**
```python
# WINDOW_SIZE = 10 was defined but then...
X_train = X_train.reshape(-1, 1, len(FEATURE_COLS))  # ← 1 timestep only!
```
The LSTM gets a single snapshot instead of 10 cycles of history.
It's like asking a doctor to predict your health from one blood test instead of 10.

**Bug #2: RUL in raw days, not normalized**
```
aaa.ipynb: target = cycles / 167  → range 0.0 to 1.0  → easy to learn
01_battery: target = raw days     → range 0 to 2520   → 15x harder to learn
```
Neural networks learn much better when targets are in the range 0→1.

### Results
| Metric | Value | Target |
|--------|-------|--------|
| MAE    | **698 days** ❌ | < 30 days |
| R²     | **-0.44** ❌ | > 0.90 |

> **Why does it fail?** 1 timestep + unnormalized 2520-day target.

---

## ⚖️ Which Is Better For Your Pacemaker?

| Criterion | Simple (aaa) | PINN (01_battery) |
|-----------|-------------|-------------------|
| Works right now | ✅ Yes | ❌ No (bugs) |
| Interpretable physics | ❌ No | ✅ Yes (learns R, K, A, B) |
| Reliable with little data | ❌ Risky | ✅ Better (physics helps) |
| Aligns with Chapter 5 thesis | ❌ No | ✅ Yes (Shepherd equation cited) |
| Medical device trustworthiness | ❌ Black box | ✅ Explainable |

### 🏆 Verdict: **PINN is better for your use case — but it must be fixed.**

**Why?** For a medical device like a pacemaker:
1. **Regulators** (FDA, CE) want to know *why* the AI says 300 days remain — the Shepherd parameters (R, K, A, B) give a physical explanation.
2. **Doctors** trust a model that says "resistance increased by 0.25 Ω, indicating battery end-of-life" more than a black-box "score of 0.3."
3. **Your thesis (Chapter 5)** already cites the Shepherd equation — using the PINN is academically correct.

The simple model is a great **baseline to compare against**, but PINN is your final goal.

---

## 🔧 What the Fixed `01_battery_training.ipynb` Will Do

The rewritten notebook will:
1. **Mount Google Drive** → load CSV from `TwinPacemaker/NASA Battery Dataset/`
2. **Proper 30-step windows** (like aaa.ipynb — fix Bug #1)
3. **Normalize RUL to 0→1** (fix Bug #2)
4. **Keep the PINN physics loss** (the scientifically valuable part)
5. **Simple LSTM architecture** (128→64→32) that can actually converge
6. **Output**: `battery_pinn_lstm.keras` + `battery_rul_model_info.json` saved to Google Drive

**Expected results after fix:**
- MAE: ~10–20 cycles
- R²: ~0.80+
- Physics parameters (R, K, A, B) that match real battery degradation curves
