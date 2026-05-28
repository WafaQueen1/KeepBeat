# Data Model: Finalize TwinPacemaker Digital Twin Platform

## Entities

### Patient

- `id`: Stable patient identifier.
- `doctor_id`: Assigned clinician.
- `full_name`: Display name.
- `email`: Login/contact identifier.
- `status`: Approval state.
- `medical_id`: Optional medical/demo identifier.

### Doctor

- `id`: Stable doctor identifier.
- `full_name`: Display name.
- `email`: Login identifier.
- `status`: Approval state.

### TelemetryReading

- `id`: Unique reading identifier.
- `patient_id`: Patient owner.
- `sensor_type`: `ecg`, `cgm`, `pacemaker`, `battery`, or derived type.
- `value`: Numeric value when scalar.
- `unit`: Explicit unit, for example `bpm`, `mg_dL`, `g_L`, `percent`, `mV`.
- `timestamp`: Source or ingestion timestamp.
- `source`: `simulator`, `mobile_edge`, `cloud`, or `manual_demo`.
- `raw_payload`: Original payload for trace/debug.
- `quality`: `ok`, `degraded`, `invalid`, or `unknown`.

### AlertEvent

- `id`: Unique alert identifier.
- `patient_id`: Patient owner.
- `severity`: `info`, `warning`, `critical`.
- `category`: `glucose`, `cardiac`, `battery`, `connectivity`, `model`.
- `message`: Human-readable alert.
- `recommendation`: Demo-safe recommendation text.
- `trigger_reading_id`: Optional telemetry reference.
- `created_at`: Alert timestamp.
- `acknowledged_at`: Optional clinician/patient acknowledgment timestamp.

### EdgeAnalysisResult

- `id`: Unique result identifier.
- `patient_id`: Patient owner.
- `algorithm`: `pan_tompkins`, `glucose_thresholds`, or other edge algorithm.
- `input_window_start` / `input_window_end`: Time range processed.
- `features`: Structured output such as R-peaks, HRV hints, glucose state.
- `quality`: Processing confidence/quality status.
- `created_at`: Processing timestamp.

### ModelPrediction

- `id`: Unique prediction identifier.
- `patient_id`: Patient owner.
- `prediction_type`: `battery_rul`, `cardiac_risk`, `metabolic_risk`.
- `value`: Numeric or categorical output.
- `confidence`: Optional confidence/quality score.
- `model_name`: Algorithm/model family.
- `model_version`: Version or `demo-fallback`.
- `input_window_start` / `input_window_end`: Telemetry range used.
- `is_clinically_validated`: Boolean, default false unless evidence exists.
- `created_at`: Prediction timestamp.

## Relationships

- One doctor can have many patients.
- One patient can have many telemetry readings.
- Alerts can be created from telemetry readings, edge analysis results, or model predictions.
- Model predictions must reference a patient and should include input window metadata.

## Validation Rules

- Glucose values must include explicit unit metadata.
- Battery percentages must be clamped or rejected outside 0 to 100.
- AI predictions must include model metadata and clinical-validation status.
- Alerts must preserve the triggering category and severity.
