"""Generate and train a stacked LSTM for glucose-insulin dynamics.

This module supports `notebooks/04_train_metabolic.ipynb`.

It uses a synthetic Bergman minimal model dataset:
    G: blood glucose in mg/dL
    X: insulin action
    I: plasma insulin in microU/mL
    D(t): meal/exercise disturbance

Default CLI settings are intentionally smaller for smoke tests. Use
`--patients 10000` in Colab for the full experiment.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.integrate import odeint


WINDOW_MINUTES = 120
PREDICTION_HORIZON_MINUTES = 60
DAY_MINUTES = 1440


@dataclass(frozen=True)
class MetabolicConfig:
    dataset_output: str = "data/metabolic_profiles.pkl"
    train_npz_output: str = "data/metabolic_train_test.npz"
    stats_output: str = "data/metabolic_stats.json"
    model_output: str = "models/metabolic_lstm.h5"
    info_output: str = "models/metabolic_lstm_model_info.json"
    patients: int = 10000
    samples_per_patient: int = 64
    test_fraction: float = 0.2
    random_seed: int = 42
    epochs: int = 50
    batch_size: int = 64


def bergman_model(
    y: list[float],
    t: float,
    si: float,
    sg: float,
    p2: float,
    p3: float,
    n: float,
    gamma: float,
    meals: list[tuple[float, float]],
) -> list[float]:
    """Bergman minimal model with simple meal/exercise disturbance."""
    glucose, insulin_action, insulin = y
    basal_glucose = 90.0
    basal_insulin = 10.0

    disturbance = 0.0
    for event_time, carbs in meals:
        if 0.0 <= t - event_time < 15.0:
            disturbance += carbs / 15.0

    d_glucose = -sg * (glucose - basal_glucose) - insulin_action * glucose + disturbance
    d_action = -p2 * insulin_action + p3 * (insulin - basal_insulin)
    d_insulin = -n * (insulin - basal_insulin) + gamma * max(0.0, glucose - basal_glucose)

    return [d_glucose, d_action, d_insulin]


def generate_patient_profile(rng: np.random.Generator) -> tuple[float, float, float, float, float, float]:
    """Create one random patient parameter profile with clipped physiology."""
    si = float(np.clip(rng.normal(0.3, 0.1), 0.05, 0.7))
    sg = float(np.clip(rng.normal(0.02, 0.005), 0.005, 0.05))
    p2 = float(np.clip(rng.normal(0.025, 0.005), 0.005, 0.06))
    p3 = float(np.clip(rng.normal(0.00001, 0.000002), 0.000002, 0.00003))
    n = float(np.clip(rng.normal(0.2, 0.05), 0.05, 0.4))
    gamma = float(np.clip(rng.normal(0.005, 0.001), 0.001, 0.01))
    return si, sg, p2, p3, n, gamma


def generate_daily_events(rng: np.random.Generator) -> list[tuple[float, float]]:
    meals = [
        (480.0, float(rng.integers(60, 91))),
        (780.0, float(rng.integers(50, 71))),
        (1140.0, float(rng.integers(70, 91))),
    ]
    if rng.random() > 0.5:
        exercise_time = float(rng.choice([600, 1020]))
        meals.append((exercise_time, -30.0))
    return sorted(meals, key=lambda event: event[0])


def time_since_last_meal(minute: int, events: list[tuple[float, float]]) -> float:
    previous_meals = [minute - int(event_time) for event_time, carbs in events if carbs > 0 and event_time < minute]
    return float(min(previous_meals) if previous_meals else 999)


def exercise_active(minute: int, events: list[tuple[float, float]]) -> int:
    return int(any(carbs < 0 and 0 <= minute - int(event_time) < 30 for event_time, carbs in events))


def simulate_patient_day(
    patient_id: int,
    rng: np.random.Generator,
    samples_per_patient: int,
) -> list[dict[str, Any]]:
    params = generate_patient_profile(rng)
    events = generate_daily_events(rng)
    timeline = np.linspace(0, DAY_MINUTES - 1, DAY_MINUTES)
    initial_state = [90.0, 0.0, 10.0]
    solution = odeint(bergman_model, initial_state, timeline, args=(*params, events))

    glucose = np.clip(solution[:, 0], 40.0, 350.0)
    insulin_action = solution[:, 1]
    insulin = np.clip(solution[:, 2], 0.0, 300.0)

    valid_start = WINDOW_MINUTES
    valid_end = DAY_MINUTES - PREDICTION_HORIZON_MINUTES
    candidate_indices = np.arange(valid_start, valid_end)
    sample_count = min(samples_per_patient, len(candidate_indices))
    selected = rng.choice(candidate_indices, size=sample_count, replace=False)

    rows: list[dict[str, Any]] = []
    si, sg, p2, p3, n, gamma = params
    for minute in sorted(selected.tolist()):
        target_minute = minute + PREDICTION_HORIZON_MINUTES
        rows.append(
            {
                "patient_id": patient_id,
                "minute": int(minute),
                "glucose_history": glucose[minute - WINDOW_MINUTES : minute].astype(float).tolist(),
                "insulin_history": insulin[minute - WINDOW_MINUTES : minute].astype(float).tolist(),
                "insulin_action_history": insulin_action[minute - WINDOW_MINUTES : minute].astype(float).tolist(),
                "time_since_meal": time_since_last_meal(int(minute), events),
                "exercise": exercise_active(int(minute), events),
                "target_glucose": float(glucose[target_minute]),
                "si": si,
                "sg": sg,
                "p2": p2,
                "p3": p3,
                "n": n,
                "gamma": gamma,
            }
        )
    return rows


def generate_metabolic_dataset(config: MetabolicConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.random_seed)
    all_rows: list[dict[str, Any]] = []
    for patient_id in range(config.patients):
        all_rows.extend(
            simulate_patient_day(
                patient_id=patient_id,
                rng=rng,
                samples_per_patient=config.samples_per_patient,
            )
        )

    df = pd.DataFrame(all_rows)
    Path(config.dataset_output).parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(config.dataset_output)
    return df


def prepare_arrays(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_glucose = np.asarray(df["glucose_history"].tolist(), dtype=np.float32)
    x_insulin = np.asarray(df["insulin_history"].tolist(), dtype=np.float32)
    x_timeseries = np.stack([x_glucose, x_insulin], axis=-1)
    x_meta = df[["time_since_meal", "exercise"]].to_numpy(dtype=np.float32)
    y = df["target_glucose"].to_numpy(dtype=np.float32).reshape(-1, 1)
    return x_timeseries, x_meta, y


def split_indices(n_samples: int, test_fraction: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    indices = np.arange(n_samples)
    rng.shuffle(indices)
    test_count = max(1, int(round(n_samples * test_fraction)))
    return indices[test_count:], indices[:test_count]


def normalize_arrays(
    x_ts_train: np.ndarray,
    x_ts_test: np.ndarray,
    x_meta_train: np.ndarray,
    x_meta_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    ts_mean = x_ts_train.reshape(-1, x_ts_train.shape[-1]).mean(axis=0)
    ts_std = x_ts_train.reshape(-1, x_ts_train.shape[-1]).std(axis=0)
    ts_std = np.where(ts_std == 0, 1.0, ts_std)

    meta_mean = x_meta_train.mean(axis=0)
    meta_std = x_meta_train.std(axis=0)
    meta_std = np.where(meta_std == 0, 1.0, meta_std)

    y_mean = y_train.mean(axis=0)
    y_std = y_train.std(axis=0)
    y_std = np.where(y_std == 0, 1.0, y_std)

    stats = {
        "timeseries_feature_order": ["glucose", "insulin"],
        "timeseries_mean": ts_mean.tolist(),
        "timeseries_std": ts_std.tolist(),
        "metadata_feature_order": ["time_since_meal", "exercise"],
        "metadata_mean": meta_mean.tolist(),
        "metadata_std": meta_std.tolist(),
        "target_mean": y_mean.tolist(),
        "target_std": y_std.tolist(),
    }

    return (
        (x_ts_train - ts_mean) / ts_std,
        (x_ts_test - ts_mean) / ts_std,
        (x_meta_train - meta_mean) / meta_std,
        (x_meta_test - meta_mean) / meta_std,
        (y_train - y_mean) / y_std,
        (y_test - y_mean) / y_std,
        stats,
    )


def create_train_test_arrays(
    df: pd.DataFrame,
    config: MetabolicConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    x_timeseries, x_meta, y = prepare_arrays(df)
    train_idx, test_idx = split_indices(len(df), config.test_fraction, config.random_seed)
    return normalize_arrays(
        x_timeseries[train_idx],
        x_timeseries[test_idx],
        x_meta[train_idx],
        x_meta[test_idx],
        y[train_idx],
        y[test_idx],
    )


def save_train_test_npz(
    config: MetabolicConfig,
    x_ts_train: np.ndarray,
    x_ts_test: np.ndarray,
    x_meta_train: np.ndarray,
    x_meta_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    stats: dict[str, Any],
) -> None:
    Path(config.train_npz_output).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        config.train_npz_output,
        x_ts_train=x_ts_train,
        x_ts_test=x_ts_test,
        x_meta_train=x_meta_train,
        x_meta_test=x_meta_test,
        y_train=y_train,
        y_test=y_test,
    )
    Path(config.stats_output).write_text(json.dumps(stats, indent=2), encoding="utf-8")


def load_train_test_npz(config: MetabolicConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    data = np.load(config.train_npz_output)
    with open(config.stats_output, "r", encoding="utf-8") as handle:
        stats = json.load(handle)
    return (
        data["x_ts_train"],
        data["x_ts_test"],
        data["x_meta_train"],
        data["x_meta_test"],
        data["y_train"],
        data["y_test"],
        stats,
    )


def build_metabolic_lstm():
    from tensorflow import keras
    from tensorflow.keras import layers

    ts_input = layers.Input(shape=(WINDOW_MINUTES, 2), name="timeseries_input")
    lstm = layers.LSTM(128, return_sequences=True, name="lstm_1")(ts_input)
    lstm = layers.Dropout(0.3, name="dropout_1")(lstm)
    lstm = layers.LSTM(64, return_sequences=True, name="lstm_2")(lstm)
    lstm = layers.Dropout(0.3, name="dropout_2")(lstm)
    lstm = layers.LSTM(32, return_sequences=False, name="lstm_3")(lstm)

    meta_input = layers.Input(shape=(2,), name="metadata_input")
    meta_dense = layers.Dense(8, activation="relu", name="metadata_dense")(meta_input)

    fusion = layers.Concatenate(name="fusion")([lstm, meta_dense])
    dense = layers.Dense(16, activation="relu", name="fusion_dense")(fusion)
    dense = layers.Dropout(0.2, name="fusion_dropout")(dense)
    output = layers.Dense(1, activation="linear", name="glucose_output")(dense)

    model = keras.Model(inputs=[ts_input, meta_input], outputs=output, name="Stacked_LSTM_Metabolic_Simulation")
    model.compile(
        optimizer=keras.optimizers.Adam(0.001),
        loss="mse",
        metrics=["mae"],
    )
    return model


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.ravel(y_true) - np.ravel(y_pred))))


def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((np.ravel(y_true) - np.ravel(y_pred)) ** 2)))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    true = np.ravel(y_true).astype(float)
    pred = np.ravel(y_pred).astype(float)
    ss_res = float(np.sum((true - pred) ** 2))
    ss_tot = float(np.sum((true - np.mean(true)) ** 2))
    return float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")


def denormalize_target(y_norm: np.ndarray, stats: dict[str, Any]) -> np.ndarray:
    mean = np.asarray(stats["target_mean"], dtype=float)
    std = np.asarray(stats["target_std"], dtype=float)
    return y_norm * std + mean


def prepare_metabolic_dataset(config: MetabolicConfig) -> dict[str, Any]:
    df = generate_metabolic_dataset(config)
    arrays = create_train_test_arrays(df, config)
    save_train_test_npz(config, *arrays)
    stats = arrays[-1]
    stats.update(
        {
            "samples": int(len(df)),
            "patients": config.patients,
            "samples_per_patient": config.samples_per_patient,
            "window_minutes": WINDOW_MINUTES,
            "prediction_horizon_minutes": PREDICTION_HORIZON_MINUTES,
            "test_fraction": config.test_fraction,
        }
    )
    Path(config.stats_output).write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return stats


def train_metabolic_lstm(config: MetabolicConfig) -> dict[str, Any]:
    import tensorflow as tf
    from tensorflow import keras

    tf.keras.utils.set_random_seed(config.random_seed)

    if not Path(config.train_npz_output).exists() or not Path(config.stats_output).exists():
        prepare_metabolic_dataset(config)

    x_ts_train, x_ts_test, x_meta_train, x_meta_test, y_train, y_test, stats = load_train_test_npz(config)
    model = build_metabolic_lstm()

    history = model.fit(
        [x_ts_train, x_meta_train],
        y_train,
        validation_data=([x_ts_test, x_meta_test], y_test),
        epochs=config.epochs,
        batch_size=config.batch_size,
        callbacks=[
            keras.callbacks.EarlyStopping(
                monitor="val_mae",
                patience=10,
                restore_best_weights=True,
            )
        ],
        verbose=1,
    )

    y_pred_norm = model.predict([x_ts_test, x_meta_test], verbose=0)
    y_pred = denormalize_target(y_pred_norm, stats)
    y_true = denormalize_target(y_test, stats)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    model_path = Path(config.model_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)

    info = {
        "model_name": "Stacked_LSTM_Metabolic_Simulation",
        "model_file": str(model_path),
        "mae_mg_dl": mae,
        "target_mae_mg_dl": 12.0,
        "rmse_mg_dl": rmse,
        "target_rmse_mg_dl": 18.0,
        "r2_score": r2,
        "target_r2": 0.92,
        "target_met": bool(mae < 12.0 and rmse < 18.0 and r2 > 0.92),
        "input_shapes": {
            "timeseries_input": [WINDOW_MINUTES, 2],
            "metadata_input": [2],
        },
        "feature_order": {
            "timeseries_input": ["glucose_history", "insulin_history"],
            "metadata_input": ["time_since_meal", "exercise"],
        },
        "epochs_requested": config.epochs,
        "epochs_trained": len(history.history.get("loss", [])),
        "train_samples": int(len(x_ts_train)),
        "test_samples": int(len(x_ts_test)),
        "stats": stats,
        "training_config": asdict(config),
        "modeling_note": "Synthetic Bergman Minimal Model data; not patient-validated CGM/insulin therapy data.",
    }

    info_path = Path(config.info_output)
    info_path.parent.mkdir(parents=True, exist_ok=True)
    info_path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--dataset-output", default="data/metabolic_profiles.pkl")
    parser.add_argument("--train-npz-output", default="data/metabolic_train_test.npz")
    parser.add_argument("--stats-output", default="data/metabolic_stats.json")
    parser.add_argument("--model-output", default="models/metabolic_lstm.h5")
    parser.add_argument("--info-output", default="models/metabolic_lstm_model_info.json")
    parser.add_argument("--patients", type=int, default=10000)
    parser.add_argument("--samples-per-patient", type=int, default=64)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = MetabolicConfig(
        dataset_output=args.dataset_output,
        train_npz_output=args.train_npz_output,
        stats_output=args.stats_output,
        model_output=args.model_output,
        info_output=args.info_output,
        patients=args.patients,
        samples_per_patient=args.samples_per_patient,
        test_fraction=args.test_fraction,
        random_seed=args.random_seed,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )

    if args.prepare_only:
        stats = prepare_metabolic_dataset(config)
        print(json.dumps(stats, indent=2))
        return

    info = train_metabolic_lstm(config)
    print("=" * 60)
    print("METABOLIC LSTM - FINAL METRICS")
    print("=" * 60)
    print(f"MAE: {info['mae_mg_dl']:.2f} mg/dL (Target: <12 mg/dL)")
    print(f"RMSE: {info['rmse_mg_dl']:.2f} mg/dL (Target: <18 mg/dL)")
    print(f"R2: {info['r2_score']:.4f} (Target: >0.92)")
    print(f"Model saved: {info['model_file']}")
    print(f"Model info saved: {config.info_output}")


if __name__ == "__main__":
    main()
