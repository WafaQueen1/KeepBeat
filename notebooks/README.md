# Smart TwinPac Training Notebooks

Use these notebooks in Google Colab free tier. Keep datasets and exported `.h5` artifacts outside git unless they are small enough and explicitly approved.

## Order

1. `01_battery_dataset_cleaning.ipynb` - NASA discharge-only battery preparation for pacemaker RUL.
2. `02_train_battery_rul.ipynb` - PINN-LSTM battery RUL training.
3. `03_train_cardiac_risk.ipynb` - Bidirectional LSTM cardiac risk training.
4. `04_train_metabolic.ipynb` - Stacked LSTM metabolic simulation training.

## Battery CSV Output

The first notebook exports:

```text
data/battery_train.csv
data/battery_test.csv
data/battery_stats.json
```

Expected CSV columns:

```text
sequence_id, source_battery_id, timestep, month, voltage_v, current_a,
temperature_c, capacity_ah, soc_pct, soh_pct, rul_days, rul_months,
eol_label, augmented
```

## Battery RUL Model Output

The second notebook exports:

```text
models/battery_rul_pinn_lstm.h5
models/battery_rul_model_info.json
```

The model expects `(batch, 180, 3)` inputs with this feature order:

```text
voltage_v, temperature_c, current_a
```

## Metabolic Simulation Output

The fourth notebook generates synthetic Bergman Minimal Model data and exports:

```text
data/metabolic_profiles.pkl
data/metabolic_train_test.npz
data/metabolic_stats.json
models/metabolic_lstm.h5
models/metabolic_lstm_model_info.json
```

The model expects two inputs:

```text
timeseries_input: (batch, 120, 2) -> glucose_history, insulin_history
metadata_input: (batch, 2) -> time_since_meal, exercise
```
