"""Multi-level glucose threshold analyzer with persistence checks."""

from __future__ import annotations

import time
from collections import deque
from typing import Deque


class GlucoseAnalyzer:
    """Analyze CGM glucose values in g/L."""

    def __init__(
        self,
        hypo_threshold: float = 0.7,
        hyper_threshold: float = 1.8,
        persistence_window: float = 120,
    ):
        self.hypo_threshold = hypo_threshold
        self.hyper_threshold = hyper_threshold
        self.persistence_window = persistence_window
        self.history: Deque[tuple[float, float]] = deque(maxlen=300)
        self.current_state = "normal"
        self.alert_start_time: float | None = None
        self.pending_state = "normal"

    def analyze(self, glucose_value: float, timestamp: float | None = None) -> dict:
        """Analyze one glucose reading."""
        if timestamp is None:
            timestamp = time.time()
        glucose = float(glucose_value)
        self.history.append((timestamp, glucose))

        instant_state = self._instant_state(glucose)
        confirmed = False

        if instant_state != "normal":
            if self.alert_start_time is None or instant_state != self.pending_state:
                self.alert_start_time = timestamp
                self.pending_state = instant_state

            duration = timestamp - self.alert_start_time
            if duration >= self.persistence_window:
                confirmed = True
                self.current_state = instant_state
            else:
                self.current_state = instant_state
        else:
            self.alert_start_time = None
            self.pending_state = "normal"
            self.current_state = "normal"

        severity = self._determine_severity(glucose, confirmed)
        recommendation = self._generate_recommendation(self.current_state, glucose, severity)

        return {
            "state": self.current_state,
            "alert": confirmed,
            "severity": severity,
            "recommendation": recommendation,
            "timestamp": timestamp,
            "glucose_value": glucose,
        }

    def _instant_state(self, glucose: float) -> str:
        if glucose < self.hypo_threshold:
            return "hypoglycemia"
        if glucose > self.hyper_threshold:
            return "hyperglycemia"
        return "normal"

    def _determine_severity(self, glucose: float, confirmed: bool) -> str | None:
        if not confirmed:
            return None
        if glucose <= 0.6 or glucose >= 2.0:
            return "critical"
        if glucose < self.hypo_threshold or glucose > self.hyper_threshold:
            return "warning"
        return None

    def _generate_recommendation(self, state: str, glucose: float, severity: str | None) -> str:
        if state == "hypoglycemia":
            if severity == "critical":
                return (
                    "URGENCE: Hypoglycemie critique (<0.6 g/L). "
                    "Consommer 15g glucose immediatement. S'asseoir. "
                    "Retester dans 15 min. Appeler secours si symptomes persistent."
                )
            return (
                "ATTENTION: Hypoglycemie detectee (<0.7 g/L). "
                "Consommer 10g glucose. Verifier dans 15 min."
            )

        if state == "hyperglycemia":
            if severity == "critical":
                return (
                    "URGENCE: Hyperglycemie critique (>2.0 g/L). "
                    "Hydratation immediate. Contacter medecin."
                )
            return (
                "ATTENTION: Hyperglycemie detectee (>1.8 g/L). "
                "Reduire apport glucidique. Surveiller."
            )

        return "Glycemie normale. Continuer surveillance."

    def check_correlation_with_ecg(self, glucose: float, heart_rate: float) -> bool:
        """Detect critical glucose/ECG combinations."""
        if glucose < 0.7 and heart_rate < 50:
            return True
        if glucose > 1.5 and heart_rate > 100:
            return True
        return False


if __name__ == "__main__":
    analyzer = GlucoseAnalyzer()
    readings = [0.9, 0.85, 0.75, 0.68, 0.65, 0.62, 0.60]
    start = time.time()

    for i, glucose in enumerate(readings):
        result = analyzer.analyze(glucose, timestamp=start + i * 60)
        print(
            f"t={i}min: {glucose} g/L -> {result['state']} "
            f"(alert={result['alert']}, severity={result['severity']})"
        )
        print(f"  -> {result['recommendation']}")
