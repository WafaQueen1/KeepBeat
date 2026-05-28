# MQTT Contracts

## Topics

- `cgm/glucose`
- `pacemaker/battery`
- `pacemaker/ecg`
- `edge/alerts`

## CGM Payload

```json
{
  "patient_id": "pat_jenkins_001",
  "glucose_level": 0.82,
  "unit": "g_L",
  "timestamp": "2026-05-13T10:00:00Z"
}
```

## Pacemaker Battery Payload

```json
{
  "patient_id": "pat_jenkins_001",
  "battery_level_percent": 88.4,
  "rul_cycles": 1200,
  "timestamp": "2026-05-13T10:00:00Z"
}
```

## ECG Payload

```json
{
  "patient_id": "pat_jenkins_001",
  "sample_rate_hz": 250,
  "unit": "mV",
  "samples": [0.01, 0.02, 0.12],
  "timestamp": "2026-05-13T10:00:00Z"
}
```

## Alert Payload

```json
{
  "patient_id": "pat_jenkins_001",
  "severity": "warning",
  "category": "glucose",
  "message": "Glucose threshold crossed",
  "recommendation": "Follow the demo recovery plan and contact a clinician if symptoms occur.",
  "timestamp": "2026-05-13T10:00:00Z"
}
```
