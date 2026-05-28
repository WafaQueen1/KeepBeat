# Data Layout

Place NASA battery `.mat` files here before running the preparation script.

```text
data/
|-- raw/
|   `-- nasa_battery/
|       |-- B0005.mat
|       |-- B0006.mat
|       |-- B0007.mat
|       `-- B0018.mat
`-- processed/
    `-- optional intermediate exports
```

The NASA files are not committed to the repository. Download them from the NASA Prognostics repository or the Kaggle mirror, then run:

```bash
python backend/ml/prepare_nasa_battery_dataset.py
```

The exported files are:

```text
data/battery_train.csv
data/battery_test.csv
data/battery_stats.json
```

The exported CSVs keep only discharge curves, remap battery aging to an 84-month pacemaker lifetime, normalize/interpolate to 37 C body temperature, and add augmented sequences for LSTM training. This is a prototype dataset transformation for RUL modeling, not a validated Li-CFx pacemaker chemistry model.
