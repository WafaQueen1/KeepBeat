# API Contracts

## Telemetry Ingestion

`POST /api/v1/telemetry`

Request:

```json
{
  "patient_id": "pat_jenkins_001",
  "sensor_type": "cgm",
  "value": 0.82,
  "unit": "g_L",
  "timestamp": "2026-05-13T10:00:00Z",
  "source": "simulator",
  "raw_payload": {}
}
```

Response:

```json
{
  "id": "telemetry_001",
  "status": "accepted",
  "quality": "ok"
}
```

## Telemetry Retrieval

`GET /api/v1/telemetry/{patient_id}?limit=100`

Response:

```json
{
  "patient_id": "pat_jenkins_001",
  "readings": []
}
```

## Model Prediction

`POST /api/v1/predictions/{prediction_type}`

Allowed prediction types:

- `battery_rul`
- `cardiac_risk`
- `metabolic_risk`

Response:

```json
{
  "patient_id": "pat_jenkins_001",
  "prediction_type": "battery_rul",
  "value": 120.5,
  "unit": "cycles",
  "confidence": 0.72,
  "model_name": "lstm_pinn_rul",
  "model_version": "demo-fallback",
  "is_clinically_validated": false
}
```
