# Quickstart: Smart TwinPac Docker Telemetry Demo

## Prerequisites

- Docker Desktop running.
- PowerShell terminal from the repository root.

## Start Full Docker Stack

```powershell
cd "D:\Vibe Coding\TwinPacemaker"
docker compose up --build -d
```

Expected services:

- FastAPI Backend: `http://localhost:8000`
- MQTT TCP: `1883`
- MQTT WebSocket: `9001`
- TimescaleDB/PostgreSQL: host `5432`, container `5432`
- MQTT Subscriber: background worker container

## Verify Containers

```powershell
docker compose ps
docker compose logs --tail=80 backend mqtt_subscriber
```

Expected:

- `twinpac_timescaledb` is healthy.
- `twinpac_mqtt` is healthy.
- `twinpac_backend` is up.
- `twinpac_mqtt_subscriber` logs `Connected to MQTT broker`.

## Publish Test Telemetry

PowerShell can mangle JSON passed directly to `mosquitto_pub`. Use Python inside the Docker network for reliable JSON publishing:

```powershell
docker exec twinpac_mqtt_subscriber python -c "import json, paho.mqtt.publish as publish; publish.single('twinpac/patient/PAT001/battery', payload=json.dumps({'voltage':3.42}), hostname='mosquitto')"
```

```powershell
docker exec twinpac_mqtt_subscriber python -c "import json, paho.mqtt.publish as publish; publish.single('twinpac/patient/PAT001/glucose', payload=json.dumps({'glucose':0.6}), hostname='mosquitto')"
```

```powershell
docker exec twinpac_mqtt_subscriber python -c "import json, paho.mqtt.publish as publish; publish.single('twinpac/patient/PAT001/heartrate', payload=json.dumps({'heart_rate':75}), hostname='mosquitto')"
```

## Verify Subscriber Stored Data

```powershell
docker compose logs --tail=120 mqtt_subscriber
```

Expected log lines:

- `Received MQTT message on twinpac/patient/PAT001/...`
- `Stored twinpac/patient/PAT001/...`

```powershell
docker exec twinpac_timescaledb psql -U twinpac -d twinpac_db -c "SELECT 'ecg' AS table_name, count(*) FROM ecg_telemetry UNION ALL SELECT 'glucose', count(*) FROM glucose_telemetry UNION ALL SELECT 'battery', count(*) FROM battery_telemetry;"
```

Expected counts: at least one row in each telemetry table after the three publishes.

## Query FastAPI

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health | ConvertTo-Json -Depth 5
```

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/v1/dashboard/PAT001 | ConvertTo-Json -Depth 8
```

Expected dashboard fields:

- `ecg.heart_rate` is `75`
- `glucose.level` is `0.6`
- `battery.voltage` is `3.42`

## Stop Stack

```powershell
docker compose down
```

## Demo Safety Note

All predictive outputs are research/demo support unless trained model artifacts, validation metrics, and clinical review evidence are supplied.
