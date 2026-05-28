"""MQTT subscriber service.

Listens to Smart TwinPac telemetry topics and stores analyzed readings in the
database.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import MQTT_BROKER, MQTT_CLIENT_ID, MQTT_PASSWORD, MQTT_PORT, MQTT_TOPICS, MQTT_USERNAME
from backend.database import SessionLocal, init_db
from backend.services.telemetry_storage_service import TelemetryStorageService


telemetry_service = TelemetryStorageService()


def _topic_kind(topic: str) -> str:
    return topic.split("/")[-1]


def _patient_id_from_topic(topic: str) -> str:
    parts = topic.split("/")
    if len(parts) < 4 or parts[0] != "twinpac" or parts[1] != "patient":
        raise ValueError(f"Unsupported topic format: {topic}")
    return parts[2]


def _timestamp(payload: dict) -> float:
    return float(payload.get("timestamp", datetime.now(timezone.utc).timestamp()))


def telemetry_from_payload(topic: str, payload: dict) -> tuple[str, dict]:
    """Map MQTT topic/payload to the edge service telemetry format."""
    patient_id = _patient_id_from_topic(topic)
    kind = _topic_kind(topic)
    timestamp = _timestamp(payload)

    if kind == "heartrate":
        return patient_id, {
            "timestamp": timestamp,
            "ecg_samples": payload.get("ecg_samples", []),
            "heart_rate": payload.get("heart_rate", payload.get("heartRate")),
        }
    if kind == "glucose":
        return patient_id, {
            "timestamp": timestamp,
            "glucose_value": payload.get("glucose", payload.get("glucose_value", payload.get("value"))),
        }
    if kind == "battery":
        return patient_id, {
            "timestamp": timestamp,
            "battery_voltage": payload.get("voltage", payload.get("battery_voltage", payload.get("value"))),
        }

    raise ValueError(f"Unsupported telemetry topic: {topic}")


def on_connect(client, userdata, flags, rc):
    """Subscribe to telemetry topics after connection."""
    if rc == 0:
        print("Connected to MQTT broker", flush=True)
        for topic in MQTT_TOPICS:
            client.subscribe(topic)
            print(f"Subscribed to: {topic}", flush=True)
    else:
        print(f"MQTT connection failed with code {rc}", flush=True)


def on_message(client, userdata, msg):
    """Handle one MQTT telemetry message."""
    db = None
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"Received MQTT message on {topic}: {payload}", flush=True)
        patient_id, telemetry = telemetry_from_payload(topic, payload)

        db = SessionLocal()
        analysis = telemetry_service.process_and_store(db, patient_id, telemetry)
        print(f"Stored {topic} for patient {patient_id}: {analysis}", flush=True)
    except Exception as exc:
        print(f"Error processing MQTT message: {exc}", flush=True)
        if db is not None:
            db.rollback()
    finally:
        if db is not None:
            db.close()


def main() -> None:
    """Run blocking MQTT subscriber loop."""
    import paho.mqtt.client as mqtt

    init_db()
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    if MQTT_USERNAME or MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    print(f"MQTT subscriber started (broker={MQTT_BROKER}:{MQTT_PORT})", flush=True)
    print("Listening for telemetry...", flush=True)
    client.loop_forever()


if __name__ == "__main__":
    main()
