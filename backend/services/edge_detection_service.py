"""Real-time edge detection service for incoming Smart TwinPac telemetry."""

from __future__ import annotations

import numpy as np

try:
    from backend.edge_algorithms.pan_tompkins import PanTompkinsDetector
    from backend.edge_algorithms.glucose_analyzer import GlucoseAnalyzer
    from backend.edge_algorithms.coulomb_counter import CoulombCounter
except ImportError:  # pragma: no cover - supports running from backend/ cwd
    from edge_algorithms.pan_tompkins import PanTompkinsDetector
    from edge_algorithms.glucose_analyzer import GlucoseAnalyzer
    from edge_algorithms.coulomb_counter import CoulombCounter


class EdgeDetectionService:
    """Process real-time telemetry through deterministic edge algorithms."""

    def __init__(self):
        self.ecg_detector = PanTompkinsDetector(sampling_rate=250)
        self.glucose_analyzer = GlucoseAnalyzer()
        self.battery_counter = CoulombCounter()

    def process_telemetry(self, telemetry_data: dict) -> dict:
        """Analyze incoming telemetry and return detections/alerts."""
        results: dict = {}

        if "ecg_samples" in telemetry_data and telemetry_data["ecg_samples"]:
            r_peaks, hr, arrhythmia = self.ecg_detector.detect_r_peaks(
                np.asarray(telemetry_data["ecg_samples"], dtype=float)
            )
            results["ecg"] = {
                "heart_rate": hr,
                "arrhythmia": arrhythmia,
                "r_peak_count": len(r_peaks),
                "r_peaks": r_peaks,
            }
        elif "heart_rate" in telemetry_data and telemetry_data["heart_rate"] is not None:
            results["ecg"] = {
                "heart_rate": float(telemetry_data["heart_rate"]),
                "arrhythmia": "normal",
                "r_peak_count": 0,
                "r_peaks": [],
            }

        if "glucose_value" in telemetry_data and telemetry_data["glucose_value"] is not None:
            glucose_result = self.glucose_analyzer.analyze(
                float(telemetry_data["glucose_value"]),
                telemetry_data.get("timestamp"),
            )
            results["glucose"] = glucose_result

        if "battery_voltage" in telemetry_data and telemetry_data["battery_voltage"] is not None:
            voltage = float(telemetry_data["battery_voltage"])
            soc = self.battery_counter.estimate_soc(voltage)
            rul = self.battery_counter.estimate_rul_days(voltage)
            status = self.battery_counter.get_health_status(soc)
            results["battery"] = {
                "soc_percent": soc,
                "rul_days": rul,
                "status": status,
                "low_battery_alert": soc < 20.0,
            }

        if "ecg" in results and "glucose" in results:
            results["critical_correlation"] = self.glucose_analyzer.check_correlation_with_ecg(
                float(telemetry_data["glucose_value"]),
                float(results["ecg"]["heart_rate"]),
            )

        return results
