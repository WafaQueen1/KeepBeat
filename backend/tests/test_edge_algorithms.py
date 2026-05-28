import sys
from pathlib import Path

import numpy as np

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
for path in (str(REPO_ROOT), str(BACKEND_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.edge_algorithms.coulomb_counter import CoulombCounter
from backend.edge_algorithms.glucose_analyzer import GlucoseAnalyzer
from backend.edge_algorithms.pan_tompkins import PanTompkinsDetector
from backend.services.edge_detection_service import EdgeDetectionService


def synthetic_ecg(fs=250, seconds=10, bpm=60):
    t = np.arange(0, seconds, 1 / fs)
    rr_s = 60 / bpm
    ecg = 0.03 * np.sin(2 * np.pi * 0.3 * t)
    for beat_time in np.arange(0.5, seconds, rr_s):
        ecg += np.exp(-0.5 * ((t - beat_time) / 0.025) ** 2)
    return ecg


def test_pan_tompkins_normal_rhythm():
    detector = PanTompkinsDetector(250)
    ecg = synthetic_ecg(fs=250, seconds=10, bpm=60)

    r_peaks, hr, arrhythmia = detector.detect_r_peaks(ecg)

    assert len(r_peaks) >= 8
    assert 55 <= hr <= 65, f"Expected ~60 bpm, got {hr}"
    assert arrhythmia == "normal"


def test_glucose_hypoglycemia_alert():
    analyzer = GlucoseAnalyzer(persistence_window=2)

    result = {}
    for i in range(5):
        result = analyzer.analyze(0.6, timestamp=i)

    assert result["state"] == "hypoglycemia"
    assert result["alert"] is True
    assert result["severity"] == "critical"


def test_coulomb_counter_linear_discharge():
    counter = CoulombCounter()

    assert counter.estimate_soc(3.7) == 100.0

    soc_half = counter.estimate_soc(3.2)
    assert 45 <= soc_half <= 55

    assert counter.estimate_soc(2.7) == 0.0


def test_edge_detection_service_integration():
    service = EdgeDetectionService()
    telemetry = {
        "ecg_samples": synthetic_ecg(fs=250, seconds=10, bpm=45).tolist(),
        "glucose_value": 0.6,
        "battery_voltage": 3.2,
        "timestamp": 1234567890,
    }

    results = service.process_telemetry(telemetry)

    assert "ecg" in results
    assert "glucose" in results
    assert "battery" in results
    assert "critical_correlation" in results
    assert results["critical_correlation"] is True
