"""Store edge-analyzed telemetry in SQLAlchemy models."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.telemetry import (
    BatteryTelemetry,
    ECGTelemetry,
    GlucoseTelemetry,
    timestamp_from_payload,
)
from backend.services.edge_detection_service import EdgeDetectionService


class TelemetryStorageService:
    """Analyze incoming telemetry and persist typed telemetry rows."""

    def __init__(self, edge_service: EdgeDetectionService | None = None):
        self.edge_service = edge_service or EdgeDetectionService()

    def process_and_store(self, db: Session, patient_id: str, telemetry_data: dict) -> dict:
        analysis = self.edge_service.process_telemetry(telemetry_data)
        timestamp = timestamp_from_payload(telemetry_data.get("timestamp"))

        if "ecg" in analysis:
            ecg = analysis["ecg"]
            db.add(
                ECGTelemetry(
                    patient_id=patient_id,
                    heart_rate=float(ecg["heart_rate"]),
                    arrhythmia_type=str(ecg["arrhythmia"]),
                    r_peak_count=int(ecg["r_peak_count"]),
                    timestamp=timestamp,
                )
            )

        if "glucose" in analysis:
            glucose = analysis["glucose"]
            db.add(
                GlucoseTelemetry(
                    patient_id=patient_id,
                    glucose_level=float(glucose["glucose_value"]),
                    alert_state=str(glucose["state"]),
                    alert_confirmed=bool(glucose["alert"]),
                    severity=glucose.get("severity"),
                    recommendation=glucose.get("recommendation"),
                    timestamp=timestamp,
                )
            )

        if "battery" in analysis:
            battery = analysis["battery"]
            db.add(
                BatteryTelemetry(
                    patient_id=patient_id,
                    voltage=float(telemetry_data["battery_voltage"]),
                    soc_percent=float(battery["soc_percent"]),
                    rul_days_local=float(battery["rul_days"]),
                    health_status=str(battery["status"]),
                    low_battery_alert=bool(battery["low_battery_alert"]),
                    timestamp=timestamp,
                )
            )

        db.commit()
        return analysis
