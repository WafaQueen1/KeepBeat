"""Pan-Tompkins QRS Detection Algorithm.

Reference: Pan & Tompkins (1985), IEEE Transactions on Biomedical Engineering.

Detects R-peaks in ECG signals for heart-rate and arrhythmia analysis. This is a
prototype implementation for simulated telemetry, not a validated clinical ECG
algorithm.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


class PanTompkinsDetector:
    """Pan-Tompkins-style ECG detector."""

    def __init__(self, sampling_rate: int = 250):
        self.fs = sampling_rate
        self.detected_peaks: list[int] = []
        self.last_detection_time = 0.0

    def bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        """Bandpass filter 5-15 Hz to reduce baseline and high-frequency noise."""
        values = np.asarray(signal, dtype=float)
        if len(values) < 16:
            return values

        nyquist = self.fs / 2.0
        low = 5.0 / nyquist
        high = 15.0 / nyquist
        b, a = butter(2, [low, high], btype="band")
        try:
            return filtfilt(b, a, values)
        except ValueError:
            return values - np.mean(values)

    def derivative(self, signal: np.ndarray) -> np.ndarray:
        """5-point derivative approximation."""
        h = np.array([1, 2, 0, -2, -1], dtype=float) / (8.0 * (1.0 / self.fs))
        return np.convolve(np.asarray(signal, dtype=float), h, mode="same")

    def squaring(self, signal: np.ndarray) -> np.ndarray:
        """Square signal to emphasize QRS/high-slope components."""
        values = np.asarray(signal, dtype=float)
        return values**2

    def moving_window_integration(
        self,
        signal: np.ndarray,
        window_size: int | None = None,
    ) -> np.ndarray:
        """Moving window integration with a default 150 ms window."""
        if window_size is None:
            window_size = max(1, int(0.15 * self.fs))

        window = np.ones(window_size, dtype=float) / window_size
        return np.convolve(np.asarray(signal, dtype=float), window, mode="same")

    def detect_r_peaks(self, ecg_signal: np.ndarray | list[float]) -> tuple[list[int], float, str]:
        """Detect R-peaks and classify rhythm.

        Args:
            ecg_signal: Raw ECG samples. Requires at least 1 second of data.

        Returns:
            Tuple of `(r_peak_indices, heart_rate_bpm, arrhythmia_type)`.
        """
        ecg = np.asarray(ecg_signal, dtype=float)
        if len(ecg) < self.fs:
            raise ValueError("Signal too short (need >=1s)")
        if not np.isfinite(ecg).all():
            raise ValueError("ECG signal contains non-finite values")

        filtered = self.bandpass_filter(ecg)
        differentiated = self.derivative(filtered)
        squared = self.squaring(differentiated)
        integrated = self.moving_window_integration(squared)

        r_peaks = self._detect_peaks(integrated, ecg)
        rr_intervals = np.diff(r_peaks) / self.fs * 1000.0

        heart_rate = 0.0
        if len(rr_intervals) > 0:
            heart_rate = float(60000.0 / np.mean(rr_intervals))

        arrhythmia = self._classify_arrhythmia(rr_intervals, heart_rate, len(ecg))
        self.detected_peaks = r_peaks
        return r_peaks, heart_rate, arrhythmia

    def _detect_peaks(self, integrated: np.ndarray, raw_ecg: np.ndarray) -> list[int]:
        refractory_samples = max(1, int(0.2 * self.fs))
        signal_span = float(np.max(integrated) - np.min(integrated))

        if signal_span <= 1e-12:
            return []

        threshold = float(np.median(integrated) + 0.35 * signal_span)
        candidates, _ = find_peaks(
            integrated,
            height=threshold,
            distance=refractory_samples,
        )

        if len(candidates) < 2:
            raw_span = float(np.max(raw_ecg) - np.min(raw_ecg))
            if raw_span <= 1e-12:
                return []
            raw_threshold = float(np.median(raw_ecg) + 0.45 * raw_span)
            candidates, _ = find_peaks(
                raw_ecg,
                height=raw_threshold,
                distance=refractory_samples,
            )

        return [int(index) for index in candidates.tolist()]

    def _classify_arrhythmia(
        self,
        rr_intervals: np.ndarray,
        heart_rate: float,
        sample_count: int | None = None,
    ) -> str:
        """Classify arrhythmia from RR intervals and heart rate."""
        if len(rr_intervals) == 0:
            duration_s = (sample_count or 0) / self.fs
            return "arrest" if duration_s >= 5.0 else "normal"

        mean_rr = float(np.mean(rr_intervals))
        std_rr = float(np.std(rr_intervals))
        coefficient_of_variation = (std_rr / mean_rr) * 100.0 if mean_rr > 0 else 0.0

        if len(rr_intervals) >= 30:
            if mean_rr < 600.0 or heart_rate > 100.0:
                return "tachycardia"
            if mean_rr > 1200.0 or heart_rate < 50.0:
                return "bradycardia"

        if coefficient_of_variation > 10.0:
            return "fibrillation"

        return "normal"


if __name__ == "__main__":
    fs = 250
    t = np.linspace(0, 10, 10 * fs)
    ecg = np.sin(2 * np.pi * 1.25 * t) + 0.3 * np.random.default_rng(42).normal(size=len(t))

    detector = PanTompkinsDetector(sampling_rate=fs)
    r_peaks, hr, arrhythmia = detector.detect_r_peaks(ecg)

    print(f"Detected {len(r_peaks)} R-peaks")
    print(f"Heart Rate: {hr:.1f} bpm")
    print(f"Arrhythmia: {arrhythmia}")
