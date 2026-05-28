"""Backend configuration for Smart TwinPac prototype services."""

from __future__ import annotations

import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres@localhost:5432/twinpacemaker",
)

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "backend_subscriber")

MQTT_TOPICS = [
    "twinpac/patient/+/heartrate",
    "twinpac/patient/+/glucose",
    "twinpac/patient/+/battery",
]
