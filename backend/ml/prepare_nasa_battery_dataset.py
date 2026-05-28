"""Prepare NASA battery data for pacemaker RUL sequence modeling.

This script backs `notebooks/01_battery_dataset_cleaning.ipynb`.

It adapts NASA Li-ion 18650 cycling data to a prototype pacemaker RUL dataset:

1. Load and inspect NASA `.mat` files.
2. Keep discharge-only phases.
3. Remap NASA cycle index to an 84-month pacemaker lifetime.
4. Normalize/interpolate voltage to 37 C body temperature conditions.
5. Calculate RUL in days until voltage crosses the end-of-life threshold.
6. Augment sequences with Gaussian noise and time warping.
7. Save train/test CSVs plus normalization/statistics JSON.

The output is for research/prototype modeling only. It is not a validated
Li-CFx pacemaker battery chemistry model.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.io import loadmat


BODY_TEMP_C = 37.0
BODY_TEMP_TOLERANCE_C = 2.0
PACEMAKER_LIFETIME_MONTHS = 84.0
DAYS_PER_MONTH = 30.0
VOLTAGE_BOL_V = 3.7
VOLTAGE_EOL_V = 2.75
MIN_SEQUENCE_MONTHS = 30


@dataclass(frozen=True)
class PreparationConfig:
    raw_dir: str
    output_train_csv: str
    output_test_csv: str
    output_stats_json: str
    batteries: list[str]
    primary_battery: str
    pacemaker_lifetime_months: float
    days_per_month: float
    body_temp_c: float
    body_temp_tolerance_c: float
    voltage_bol_v: float
    voltage_eol_v: float
    temp_voltage_coeff_v_per_c: float
    total_sequences: int
    test_fraction: float
    random_seed: int
    voltage_noise_std_v: float
    temp_noise_std_c: float
    max_time_warp_fraction: float


def _as_1d(value: object) -> np.ndarray:
    return np.ravel(np.asarray(value))


def _field(obj: object, name: str) -> object:
    if hasattr(obj, name):
        return getattr(obj, name)
    if isinstance(obj, np.ndarray) and obj.dtype.names and name in obj.dtype.names:
        return obj[name]
    raise KeyError(f"Missing MATLAB field: {name}")


def _first_mat_struct(mat: dict, battery_id: str) -> object:
    if battery_id in mat:
        return mat[battery_id]

    for key, value in mat.items():
        if key.startswith("__"):
            continue
        try:
            _field(value, "cycle")
            return value
        except Exception:
            continue
    raise ValueError(f"Could not find battery struct for {battery_id}")


def _iter_cycles(battery_struct: object) -> Iterable[object]:
    cycles = _field(battery_struct, "cycle")
    for cycle in _as_1d(cycles):
        yield cycle


def _cycle_type(cycle: object) -> str:
    try:
        return str(_as_1d(_field(cycle, "type"))[0]).lower()
    except Exception:
        return "unknown"


def _cycle_ambient_temp(cycle: object) -> float:
    try:
        return float(_as_1d(_field(cycle, "ambient_temperature"))[0])
    except Exception:
        return np.nan


def _data_field(data: object, name: str, default: float = np.nan) -> np.ndarray:
    try:
        return _as_1d(_field(data, name)).astype(float)
    except Exception:
        return np.array([default], dtype=float)


def _is_discharge(cycle: object, voltage: np.ndarray, current: np.ndarray) -> bool:
    cycle_type = _cycle_type(cycle)
    voltage_drop = len(voltage) > 1 and np.nanmedian(np.diff(voltage)) < 0
    negative_current = len(current) > 0 and np.nanmedian(current) < 0
    return cycle_type == "discharge" or negative_current or voltage_drop


def _same_length_frame(columns: dict[str, np.ndarray | float | int | str]) -> pd.DataFrame:
    max_len = max(
        len(value) if isinstance(value, np.ndarray) else 1
        for value in columns.values()
    )
    normalized: dict[str, np.ndarray] = {}
    for key, value in columns.items():
        if isinstance(value, np.ndarray):
            if len(value) == max_len:
                normalized[key] = value
            elif len(value) == 1:
                normalized[key] = np.repeat(value[0], max_len)
            else:
                x_old = np.linspace(0.0, 1.0, len(value))
                x_new = np.linspace(0.0, 1.0, max_len)
                normalized[key] = np.interp(x_new, x_old, value)
        else:
            normalized[key] = np.repeat(value, max_len)
    return pd.DataFrame(normalized)


def inspect_mat_file(mat_path: Path, battery_id: str) -> dict:
    mat = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    battery = _first_mat_struct(mat, battery_id)
    cycles = list(_iter_cycles(battery))
    cycle_types = pd.Series([_cycle_type(cycle) for cycle in cycles]).value_counts().to_dict()
    return {
        "battery_id": battery_id,
        "path": str(mat_path),
        "cycle_count": len(cycles),
        "cycle_types": cycle_types,
    }


def extract_discharge_points(mat_path: Path, battery_id: str, temp_coeff: float) -> pd.DataFrame:
    mat = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    battery = _first_mat_struct(mat, battery_id)

    frames: list[pd.DataFrame] = []
    discharge_cycle = 0
    for source_cycle, cycle in enumerate(_iter_cycles(battery), start=1):
        data = _field(cycle, "data")
        voltage = _data_field(data, "Voltage_measured")
        current = _data_field(data, "Current_measured")

        if not _is_discharge(cycle, voltage, current):
            continue

        discharge_cycle += 1
        ambient_temp = _cycle_ambient_temp(cycle)
        measured_temp = _data_field(data, "Temperature_measured", ambient_temp)
        time_s = _data_field(data, "Time")
        capacity_ah = _data_field(data, "Capacity")

        temp_c = np.where(np.isnan(measured_temp), ambient_temp, measured_temp)
        voltage_norm_37c = voltage + temp_coeff * (BODY_TEMP_C - temp_c)

        frame = _same_length_frame(
            {
                "battery_id": battery_id,
                "source_cycle": source_cycle,
                "discharge_cycle": discharge_cycle,
                "time_s_in_discharge": time_s,
                "voltage_raw_v": voltage,
                "current_raw_a": current,
                "current_discharge_a": -np.abs(current),
                "temperature_raw_c": temp_c,
                "temperature_c": BODY_TEMP_C,
                "voltage_v": voltage_norm_37c,
                "capacity_ah": capacity_ah,
            }
        )
        frames.append(frame)

    if not frames:
        raise ValueError(f"No discharge cycles found in {mat_path}")

    points = pd.concat(frames, ignore_index=True)
    points["total_discharge_cycles"] = int(points["discharge_cycle"].max())
    return points


def summarize_monthly_curve(points: pd.DataFrame, life_months: float) -> pd.DataFrame:
    cycle_summary = (
        points.groupby(["battery_id", "discharge_cycle"], as_index=False)
        .agg(
            source_cycle=("source_cycle", "min"),
            voltage_v=("voltage_v", "median"),
            current_discharge_a=("current_discharge_a", "median"),
            temperature_c=("temperature_c", "median"),
            capacity_ah=("capacity_ah", "max"),
            total_discharge_cycles=("total_discharge_cycles", "max"),
        )
        .sort_values(["battery_id", "discharge_cycle"])
    )

    frames: list[pd.DataFrame] = []
    for battery_id, group in cycle_summary.groupby("battery_id"):
        group = group.reset_index(drop=True)
        cycle_progress = (group["discharge_cycle"] - 1) / max(len(group) - 1, 1)
        group["pacemaker_month"] = cycle_progress * life_months

        monthly_axis = np.arange(0, int(life_months) + 1)
        frame = pd.DataFrame(
            {
                "battery_id": battery_id,
                "month": monthly_axis,
                "voltage_v": np.interp(monthly_axis, group["pacemaker_month"], group["voltage_v"]),
                "current_a": np.interp(
                    monthly_axis,
                    group["pacemaker_month"],
                    group["current_discharge_a"],
                ),
                "temperature_c": BODY_TEMP_C,
                "capacity_ah": np.interp(
                    monthly_axis,
                    group["pacemaker_month"],
                    group["capacity_ah"],
                ),
            }
        )
        frames.append(frame)

    monthly = pd.concat(frames, ignore_index=True)
    monthly["month"] = monthly["month"].astype(float)
    return monthly


def _end_month_for_voltage(month: np.ndarray, voltage: np.ndarray, eol_voltage: float) -> float:
    below = np.where(voltage <= eol_voltage)[0]
    if len(below) == 0:
        return float(month[-1])
    return float(month[below[0]])


def _make_sequence(
    base: pd.DataFrame,
    sequence_id: str,
    rng: np.random.Generator,
    config: PreparationConfig,
    augmented: bool,
) -> pd.DataFrame:
    base = base.sort_values("month")
    month = base["month"].to_numpy(dtype=float)
    voltage = base["voltage_v"].to_numpy(dtype=float)
    current = base["current_a"].to_numpy(dtype=float)
    capacity = base["capacity_ah"].to_numpy(dtype=float)

    if augmented:
        warp = rng.uniform(
            1.0 - config.max_time_warp_fraction,
            1.0 + config.max_time_warp_fraction,
        )
        warped_month = np.clip(month * warp, month.min(), month.max())
        warped_month = np.maximum.accumulate(warped_month)
        voltage = np.interp(month, warped_month, voltage)
        current = np.interp(month, warped_month, current)
        capacity = np.interp(month, warped_month, capacity)
        voltage = voltage + rng.normal(0.0, config.voltage_noise_std_v, size=len(voltage))
        temperature = config.body_temp_c + rng.normal(0.0, config.temp_noise_std_c, size=len(voltage))
    else:
        temperature = np.full(len(voltage), config.body_temp_c)

    voltage = np.clip(voltage, config.voltage_eol_v, config.voltage_bol_v)
    temperature = np.clip(
        temperature,
        config.body_temp_c - config.body_temp_tolerance_c,
        config.body_temp_c + config.body_temp_tolerance_c,
    )
    current = -np.abs(current)

    eol_month = _end_month_for_voltage(month, voltage, config.voltage_eol_v)
    rul_months = np.maximum(eol_month - month, 0.0)
    initial_capacity = max(float(np.nanmax(capacity)), 1e-9)
    voltage_span = config.voltage_bol_v - config.voltage_eol_v

    return pd.DataFrame(
        {
            "sequence_id": sequence_id,
            "source_battery_id": str(base["battery_id"].iloc[0]),
            "timestep": np.arange(len(month), dtype=int),
            "month": month,
            "voltage_v": voltage,
            "current_a": current,
            "temperature_c": temperature,
            "capacity_ah": capacity,
            "soc_pct": 100.0 * (voltage - config.voltage_eol_v) / voltage_span,
            "soh_pct": 100.0 * capacity / initial_capacity,
            "rul_days": rul_months * config.days_per_month,
            "rul_months": rul_months,
            "eol_label": (rul_months <= 1.0).astype(int),
            "augmented": augmented,
        }
    )


def generate_sequences(monthly: pd.DataFrame, config: PreparationConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.random_seed)
    batteries = sorted(monthly["battery_id"].unique().tolist())
    sequences: list[pd.DataFrame] = []

    for idx in range(config.total_sequences):
        battery_id = config.primary_battery if idx == 0 and config.primary_battery in batteries else rng.choice(batteries)
        base = monthly[monthly["battery_id"] == battery_id]
        sequence = _make_sequence(
            base=base,
            sequence_id=f"seq_{idx:04d}",
            rng=rng,
            config=config,
            augmented=idx != 0,
        )
        if sequence["month"].max() >= MIN_SEQUENCE_MONTHS:
            sequences.append(sequence)

    return pd.concat(sequences, ignore_index=True)


def validate_dataset(df: pd.DataFrame, config: PreparationConfig) -> dict:
    checks = {
        "voltage_range_2p7_to_3p7": bool(df["voltage_v"].between(2.7, 3.7).all()),
        "no_charge_phases_current_positive": bool((df["current_a"] <= 0).all()),
        "temperature_35_to_39": bool(df["temperature_c"].between(35.0, 39.0).all()),
        "rul_never_negative": bool((df["rul_days"] >= 0).all()),
        "sequence_length_at_least_30_months": bool(
            (df.groupby("sequence_id")["month"].max() >= MIN_SEQUENCE_MONTHS).all()
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"Dataset validation failed: {failed}")
    return checks


def compute_stats(df: pd.DataFrame, train_df: pd.DataFrame, test_df: pd.DataFrame, validation: dict) -> dict:
    feature_columns = ["month", "voltage_v", "current_a", "temperature_c", "capacity_ah", "soc_pct", "soh_pct"]
    train_stats = train_df[feature_columns].agg(["mean", "std"]).to_dict()

    monthly = (
        df.groupby(["sequence_id"], as_index=False)
        .agg(sequence_length_months=("month", "max"), final_rul_days=("rul_days", "min"))
    )
    corr_input = df[["voltage_v", "rul_days"]].dropna()
    if len(corr_input) > 1:
        corr = float(np.corrcoef(corr_input["voltage_v"], corr_input["rul_days"])[0, 1])
        r2 = corr * corr
    else:
        r2 = float("nan")

    return {
        "total_sequences": int(df["sequence_id"].nunique()),
        "train_sequences": int(train_df["sequence_id"].nunique()),
        "test_sequences": int(test_df["sequence_id"].nunique()),
        "avg_sequence_length_months": float(monthly["sequence_length_months"].mean()),
        "voltage_correlation_with_rul_r2": r2,
        "temperature_variance_sigma": float(df["temperature_c"].std()),
        "normalization": train_stats,
        "validation_checks": validation,
        "csv_schema": list(df.columns),
    }


def split_by_sequence(df: pd.DataFrame, test_fraction: float, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    sequence_ids = np.array(sorted(df["sequence_id"].unique().tolist()))
    rng = np.random.default_rng(seed)
    shuffled = sequence_ids.copy()
    rng.shuffle(shuffled)
    test_count = max(1, int(round(len(shuffled) * test_fraction)))
    test_ids = set(shuffled[:test_count].tolist())
    train_ids = set(shuffled[test_count:].tolist())
    train_df = df[df["sequence_id"].isin(train_ids)].reset_index(drop=True)
    test_df = df[df["sequence_id"].isin(test_ids)].reset_index(drop=True)
    return train_df, test_df


def prepare_dataset(config: PreparationConfig) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    raw_dir = Path(config.raw_dir)
    found_frames: list[pd.DataFrame] = []
    inspections: list[dict] = []
    missing: list[str] = []

    for battery_id in config.batteries:
        mat_path = raw_dir / f"{battery_id}.mat"
        if not mat_path.exists():
            missing.append(str(mat_path))
            continue
        inspections.append(inspect_mat_file(mat_path, battery_id))
        found_frames.append(
            extract_discharge_points(
                mat_path=mat_path,
                battery_id=battery_id,
                temp_coeff=config.temp_voltage_coeff_v_per_c,
            )
        )

    if not found_frames:
        raise FileNotFoundError(
            "No NASA .mat files found. Place B0005.mat, B0006.mat, B0007.mat, "
            f"or B0018.mat under {raw_dir}."
        )

    discharge_points = pd.concat(found_frames, ignore_index=True)
    monthly = summarize_monthly_curve(discharge_points, config.pacemaker_lifetime_months)
    sequences = generate_sequences(monthly, config)
    validation = validate_dataset(sequences, config)
    train_df, test_df = split_by_sequence(sequences, config.test_fraction, config.random_seed)
    stats = compute_stats(sequences, train_df, test_df, validation)
    stats["config"] = asdict(config)
    stats["mat_inspection"] = inspections
    stats["missing_files"] = missing
    stats["adaptation_notes"] = [
        "Only discharge phases are retained using NASA cycle type plus current/voltage heuristics.",
        "NASA cycle progression is remapped linearly to 84 pacemaker months.",
        "Voltage is normalized/interpolated to 37 C body-temperature conditions.",
        "Augmentation adds voltage +/-15 mV noise, temperature +/-0.5 C noise, and +/-10 percent time warping.",
        "RUL is days until voltage reaches the prototype EOL threshold of 2.75 V.",
    ]

    Path(config.output_train_csv).parent.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(config.output_train_csv, index=False)
    test_df.to_csv(config.output_test_csv, index=False)
    Path(config.output_stats_json).write_text(json.dumps(stats, indent=2), encoding="utf-8")

    return train_df, test_df, stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default="data/raw/nasa_battery")
    parser.add_argument("--output-train-csv", default="data/battery_train.csv")
    parser.add_argument("--output-test-csv", default="data/battery_test.csv")
    parser.add_argument("--output-stats-json", default="data/battery_stats.json")
    parser.add_argument("--batteries", nargs="+", default=["B0005", "B0006", "B0007", "B0018"])
    parser.add_argument("--primary-battery", default="B0005")
    parser.add_argument("--total-sequences", type=int, default=500)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--temp-voltage-coeff-v-per-c", type=float, default=-0.003)
    parser.add_argument("--voltage-noise-std-v", type=float, default=0.015)
    parser.add_argument("--temp-noise-std-c", type=float, default=0.5)
    parser.add_argument("--max-time-warp-fraction", type=float, default=0.10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = PreparationConfig(
        raw_dir=args.raw_dir,
        output_train_csv=args.output_train_csv,
        output_test_csv=args.output_test_csv,
        output_stats_json=args.output_stats_json,
        batteries=args.batteries,
        primary_battery=args.primary_battery,
        pacemaker_lifetime_months=PACEMAKER_LIFETIME_MONTHS,
        days_per_month=DAYS_PER_MONTH,
        body_temp_c=BODY_TEMP_C,
        body_temp_tolerance_c=BODY_TEMP_TOLERANCE_C,
        voltage_bol_v=VOLTAGE_BOL_V,
        voltage_eol_v=VOLTAGE_EOL_V,
        temp_voltage_coeff_v_per_c=args.temp_voltage_coeff_v_per_c,
        total_sequences=args.total_sequences,
        test_fraction=args.test_fraction,
        random_seed=args.random_seed,
        voltage_noise_std_v=args.voltage_noise_std_v,
        temp_noise_std_c=args.temp_noise_std_c,
        max_time_warp_fraction=args.max_time_warp_fraction,
    )
    train_df, test_df, stats = prepare_dataset(config)
    print(f"Wrote {train_df['sequence_id'].nunique()} train sequences to {config.output_train_csv}")
    print(f"Wrote {test_df['sequence_id'].nunique()} test sequences to {config.output_test_csv}")
    print(f"Wrote stats to {config.output_stats_json}")
    print(json.dumps({k: stats[k] for k in [
        "total_sequences",
        "avg_sequence_length_months",
        "voltage_correlation_with_rul_r2",
        "temperature_variance_sigma",
    ]}, indent=2))


if __name__ == "__main__":
    main()
