"""Coulomb counting for pacemaker battery state-of-charge."""

from __future__ import annotations

import numpy as np


class CoulombCounter:
    """Linear voltage-based SoC and simple RUL estimator for edge use."""

    def __init__(
        self,
        v_full: float = 3.7,
        v_empty: float = 2.7,
        capacity_ah: float = 1.85,
        nominal_current_ua: float = 10,
    ):
        self.v_full = v_full
        self.v_empty = v_empty
        self.capacity_ah = capacity_ah
        self.nominal_current_ua = nominal_current_ua
        self.total_discharged_ah = 0.0
        self.cycles_count = 0

    def estimate_soc(self, voltage: float) -> float:
        """Estimate SoC percentage from voltage."""
        measured = float(voltage)
        if measured <= self.v_empty:
            return 0.0
        if measured >= self.v_full:
            return 100.0

        soc = 100.0 * (measured - self.v_empty) / (self.v_full - self.v_empty)
        return float(max(0.0, min(100.0, soc)))

    def estimate_rul_days(self, current_voltage: float, discharge_rate_ua: float | None = None) -> float:
        """Estimate remaining days until end-of-life voltage."""
        if discharge_rate_ua is None:
            discharge_rate_ua = self.nominal_current_ua
        if discharge_rate_ua <= 0:
            raise ValueError("discharge_rate_ua must be positive")

        current_soc = self.estimate_soc(current_voltage)
        if current_soc <= 0:
            return 0.0

        remaining_ah = (current_soc / 100.0) * self.capacity_ah
        hours_remaining = remaining_ah / (discharge_rate_ua / 1e6)
        return float(hours_remaining / 24.0)

    def track_pulse(self, pulse_duration_ms: float = 1, pulse_current_ma: float = 1) -> None:
        """Track pacing pulse discharge in Ah."""
        discharge_ah = (pulse_current_ma / 1000.0) * (pulse_duration_ms / 1000.0) / 3600.0
        self.total_discharged_ah += discharge_ah

    def get_health_status(self, soc_percent: float) -> str:
        """Classify battery health from SoC."""
        soc = float(soc_percent)
        if soc > 50:
            return "healthy"
        if soc > 20:
            return "low"
        if soc > 5:
            return "critical"
        return "depleted"


if __name__ == "__main__":
    counter = CoulombCounter()
    voltages = np.linspace(3.7, 2.7, 365 * 7)

    for day, voltage in enumerate(voltages):
        soc = counter.estimate_soc(voltage)
        rul = counter.estimate_rul_days(voltage)
        status = counter.get_health_status(soc)
        if day % 365 == 0:
            year = day // 365
            print(
                f"Year {year}: V={voltage:.2f}V, SoC={soc:.1f}%, "
                f"RUL={rul:.0f} days, Status={status}"
            )
