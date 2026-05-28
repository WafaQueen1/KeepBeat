"""Train a PINN-LSTM model for Smart TwinPac battery RUL prediction.

Expected inputs:
    data/battery_train.csv
    data/battery_test.csv
    data/battery_stats.json

Expected outputs:
    models/battery_rul_pinn_lstm.h5
    models/battery_rul_model_info.json

The cleaned dataset stores monthly pacemaker-equivalent points. This module
upsamples each sequence to daily resolution before creating 180-day windows so
the model input shape is `(batch, 180, 3)` for voltage, temperature, current.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


FEATURE_COLUMNS = ["voltage_v", "temperature_c", "current_a"]
MODEL_NAME = "PINN_LSTM_Battery_RUL"


@dataclass(frozen=True)
class TrainingConfig:
    train_csv: str = "data/battery_train.csv"
    test_csv: str = "data/battery_test.csv"
    stats_json: str = "data/battery_stats.json"
    model_output: str = "models/battery_rul_pinn_lstm.h5"
    info_output: str = "models/battery_rul_model_info.json"
    window_days: int = 180
    daily_horizon_days: int = 84 * 30
    batch_size: int = 16
    epochs: int = 100
    alpha_physics: float = 0.3
    beta_prediction: float = 0.7
    initial_lr: float = 0.001
    random_seed: int = 42


def load_battery_data(config: TrainingConfig) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    train_df = pd.read_csv(config.train_csv)
    test_df = pd.read_csv(config.test_csv)
    with open(config.stats_json, "r", encoding="utf-8") as handle:
        stats = json.load(handle)
    return train_df, test_df, stats


def _feature_stats(stats: dict[str, Any], feature: str) -> tuple[float, float]:
    normalization = stats.get("normalization", {})
    feature_stats = normalization.get(feature, {})
    mean = feature_stats.get("mean")
    std = feature_stats.get("std")

    if mean is None:
        mean = stats.get(f"{feature}_mean", 0.0)
    if std is None:
        std = stats.get(f"{feature}_std", 1.0)

    std = float(std) if float(std) != 0.0 else 1.0
    return float(mean), std


def normalize(df: pd.DataFrame, stats: dict[str, Any]) -> pd.DataFrame:
    """Add normalized feature columns using battery_stats.json."""
    out = df.copy()
    for feature in FEATURE_COLUMNS:
        mean, std = _feature_stats(stats, feature)
        out[f"{feature}_norm"] = (out[feature] - mean) / std
    return out


def upsample_sequence_to_days(group: pd.DataFrame, horizon_days: int) -> pd.DataFrame:
    """Interpolate one monthly sequence onto a daily axis."""
    ordered = group.sort_values("month")
    source_days = ordered["month"].to_numpy(dtype=float) * 30.0
    target_days = np.arange(0, horizon_days + 1, dtype=float)

    daily = pd.DataFrame(
        {
            "sequence_id": str(ordered["sequence_id"].iloc[0]),
            "source_battery_id": str(ordered["source_battery_id"].iloc[0]),
            "day": target_days,
            "voltage_v_norm": np.interp(target_days, source_days, ordered["voltage_v_norm"]),
            "temperature_c_norm": np.interp(target_days, source_days, ordered["temperature_c_norm"]),
            "current_a_norm": np.interp(target_days, source_days, ordered["current_a_norm"]),
            "voltage_v": np.interp(target_days, source_days, ordered["voltage_v"]),
            "rul_days": np.interp(target_days, source_days, ordered["rul_days"]),
        }
    )
    return daily


def create_sequences(
    df: pd.DataFrame,
    stats: dict[str, Any],
    window_days: int = 180,
    horizon_days: int = 84 * 30,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create 180-day sliding windows for RUL and physics-voltage targets."""
    normalized = normalize(df, stats)
    x_windows: list[np.ndarray] = []
    y_rul: list[float] = []
    y_voltage: list[float] = []

    for _, group in normalized.groupby("sequence_id"):
        daily = upsample_sequence_to_days(group, horizon_days)
        features = daily[["voltage_v_norm", "temperature_c_norm", "current_a_norm"]].to_numpy(dtype=np.float32)
        rul = daily["rul_days"].to_numpy(dtype=np.float32)
        voltage_norm = daily["voltage_v_norm"].to_numpy(dtype=np.float32)

        for start in range(0, len(daily) - window_days):
            end = start + window_days
            x_windows.append(features[start:end])
            y_rul.append(float(rul[end]))
            y_voltage.append(float(voltage_norm[end - 1]))

    if not x_windows:
        raise ValueError(
            "No training windows created. Check sequence length and window_days."
        )

    return (
        np.asarray(x_windows, dtype=np.float32),
        np.asarray(y_rul, dtype=np.float32).reshape(-1, 1),
        np.asarray(y_voltage, dtype=np.float32).reshape(-1, 1),
    )


def build_pinn_lstm(
    input_shape: tuple[int, int] = (180, 3),
    alpha: float = 0.3,
    beta: float = 0.7,
):
    """Build the dual-output PINN-LSTM architecture."""
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    tf.keras.utils.set_random_seed(42)

    inputs = layers.Input(shape=input_shape, name="input_sequence")

    last_state = layers.Lambda(lambda x: x[:, -1, :], name="last_state")(inputs)
    physics = layers.Dense(64, activation="tanh", name="physics_1")(last_state)
    physics_features = layers.Dense(32, activation="tanh", name="physics_2")(physics)
    physics_voltage = layers.Dense(1, activation="linear", name="physics_voltage")(physics_features)

    lstm = layers.LSTM(128, return_sequences=True, name="lstm_1")(inputs)
    lstm = layers.Dropout(0.3, name="dropout_lstm_1")(lstm)
    lstm = layers.LSTM(64, return_sequences=False, name="lstm_2")(lstm)
    lstm = layers.Dropout(0.3, name="dropout_lstm_2")(lstm)
    lstm_features = layers.Dense(32, activation="relu", name="lstm_dense")(lstm)

    fusion = layers.Concatenate(name="fusion")([physics_features, lstm_features])
    fusion = layers.Dense(16, activation="relu", name="fusion_dense")(fusion)
    fusion = layers.Dropout(0.2, name="fusion_dropout")(fusion)
    rul_output = layers.Dense(1, activation="linear", name="rul_output")(fusion)

    model = keras.Model(
        inputs=inputs,
        outputs=[rul_output, physics_voltage],
        name=MODEL_NAME,
    )

    lr_schedule = keras.optimizers.schedules.ExponentialDecay(
        0.001,
        decay_steps=100,
        decay_rate=0.96,
        staircase=True,
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr_schedule),
        loss={
            "rul_output": "mae",
            "physics_voltage": "mse",
        },
        loss_weights={
            "rul_output": beta,
            "physics_voltage": alpha,
        },
        metrics={
            "rul_output": ["mae", "mse"],
            "physics_voltage": ["mse"],
        },
    )
    return model


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.ravel(y_true) - np.ravel(y_pred))))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    true = np.ravel(y_true).astype(float)
    pred = np.ravel(y_pred).astype(float)
    ss_res = float(np.sum((true - pred) ** 2))
    ss_tot = float(np.sum((true - np.mean(true)) ** 2))
    return float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")


def train_battery_rul_model(config: TrainingConfig) -> dict[str, Any]:
    import tensorflow as tf
    from tensorflow import keras

    tf.keras.utils.set_random_seed(config.random_seed)

    train_df, test_df, stats = load_battery_data(config)
    x_train, y_train, y_train_voltage = create_sequences(
        train_df,
        stats,
        window_days=config.window_days,
        horizon_days=config.daily_horizon_days,
    )
    x_test, y_test, y_test_voltage = create_sequences(
        test_df,
        stats,
        window_days=config.window_days,
        horizon_days=config.daily_horizon_days,
    )

    model = build_pinn_lstm(
        input_shape=(config.window_days, 3),
        alpha=config.alpha_physics,
        beta=config.beta_prediction,
    )

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_rul_output_mae",
            patience=15,
            restore_best_weights=True,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_rul_output_mae",
            factor=0.5,
            patience=5,
        ),
    ]

    history = model.fit(
        x_train,
        {"rul_output": y_train, "physics_voltage": y_train_voltage},
        validation_data=(
            x_test,
            {"rul_output": y_test, "physics_voltage": y_test_voltage},
        ),
        epochs=config.epochs,
        batch_size=config.batch_size,
        callbacks=callbacks,
        verbose=1,
    )

    y_pred_rul, y_pred_voltage = model.predict(x_test, verbose=0)
    mae_days = mean_absolute_error(y_test, y_pred_rul)
    r2 = r2_score(y_test, y_pred_rul)
    physics_mse = float(np.mean((np.ravel(y_test_voltage) - np.ravel(y_pred_voltage)) ** 2))

    model_path = Path(config.model_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)

    model_info = {
        "model_name": MODEL_NAME,
        "model_file": str(model_path),
        "mae_days": mae_days,
        "target_mae_days": 30.0,
        "target_met": bool(mae_days < 30.0),
        "r2_score": r2,
        "target_r2": 0.90,
        "physics_voltage_mse": physics_mse,
        "input_shape": [config.window_days, 3],
        "window_days": config.window_days,
        "feature_order": FEATURE_COLUMNS,
        "normalization": stats.get("normalization", {}),
        "physics_weight_alpha": config.alpha_physics,
        "prediction_weight_beta": config.beta_prediction,
        "epochs_requested": config.epochs,
        "epochs_trained": len(history.history.get("loss", [])),
        "train_windows": int(len(x_train)),
        "test_windows": int(len(x_test)),
        "architecture": {
            "physics_branch": "last_state -> Dense(64,tanh) -> Dense(32,tanh) -> voltage residual output",
            "lstm_branch": "LSTM(128,seq) -> Dropout(0.3) -> LSTM(64) -> Dropout(0.3) -> Dense(32,relu)",
            "fusion": "Concatenate physics_features and lstm_features -> Dense(16,relu) -> Dropout(0.2) -> RUL",
            "loss": "0.3 * voltage MSE + 0.7 * RUL MAE",
        },
        "physics_note": (
            "The physics branch is a Shepherd-model proxy: it learns a voltage "
            "residual constrained by discharge voltage behavior rather than a "
            "fully identified electrochemical parameter set."
        ),
        "training_config": asdict(config),
    }

    info_path = Path(config.info_output)
    info_path.parent.mkdir(parents=True, exist_ok=True)
    info_path.write_text(json.dumps(model_info, indent=2), encoding="utf-8")
    return model_info


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-csv", default="data/battery_train.csv")
    parser.add_argument("--test-csv", default="data/battery_test.csv")
    parser.add_argument("--stats-json", default="data/battery_stats.json")
    parser.add_argument("--model-output", default="models/battery_rul_pinn_lstm.h5")
    parser.add_argument("--info-output", default="models/battery_rul_model_info.json")
    parser.add_argument("--window-days", type=int, default=180)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--alpha-physics", type=float, default=0.3)
    parser.add_argument("--beta-prediction", type=float, default=0.7)
    parser.add_argument("--random-seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = TrainingConfig(
        train_csv=args.train_csv,
        test_csv=args.test_csv,
        stats_json=args.stats_json,
        model_output=args.model_output,
        info_output=args.info_output,
        window_days=args.window_days,
        batch_size=args.batch_size,
        epochs=args.epochs,
        alpha_physics=args.alpha_physics,
        beta_prediction=args.beta_prediction,
        random_seed=args.random_seed,
    )
    info = train_battery_rul_model(config)
    print("=" * 60)
    print("BATTERY RUL MODEL - FINAL METRICS")
    print("=" * 60)
    print(f"Test MAE: {info['mae_days']:.2f} days (Target: <30 days)")
    print(f"Test R2: {info['r2_score']:.4f} (Target: >0.90)")
    print(f"Physics voltage MSE: {info['physics_voltage_mse']:.6f}")
    print(f"Physics Loss Weight alpha: {info['physics_weight_alpha']}")
    print(f"Prediction Loss Weight beta: {info['prediction_weight_beta']}")
    print(f"Model saved: {info['model_file']}")
    print(f"Model info saved: {config.info_output}")


if __name__ == "__main__":
    main()
