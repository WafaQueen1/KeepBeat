# Smart TwinPac Digital Twin Prototype Constitution

## Core Principles

### I. Prototype Scope First

Smart TwinPac is currently a research/prototype system, not a regulated medical product. All implementation work MUST prioritize the first working hierarchical Digital Twin prototype for pacemaker monitoring: simulated sensors, MQTT data flow, FastAPI backend, TimescaleDB persistence, edge algorithms, and cloud AI inference endpoints.

The project MUST NOT expand into chatbot/NLP features, real ESP32 firmware, mobile UI redesign, or production-grade authentication beyond basic bcrypt password hashing during this phase.

### II. Data Pipeline Before Intelligence

No AI, dashboard, or analytics task is considered complete unless the telemetry pipeline is operational first:

`Simulated sensors -> MQTT -> Backend subscriber/API -> TimescaleDB -> Prediction API/Dashboard`

Telemetry payloads MUST include patient identity, sensor type, timestamp, value, units, source, and processing status. Unit handling MUST be explicit, especially for glucose and battery state-of-charge.

### III. Edge Safety Algorithms Are Deterministic

Edge logic MUST be deterministic, testable, and fast. The required edge algorithms are:

- Pan-Tompkins-style ECG processing for arrhythmia detection in less than 1 second.
- Multi-threshold glucose analysis with persistence rules for hypoglycemia detection in less than 2 seconds.
- Coulomb-counting battery state-of-charge estimation with critical alert below 20 percent SoC.

Edge outputs MUST be treated as prototype/research alerts, not validated clinical decisions.

### IV. Cloud AI Models Are Versioned Artifacts

Cloud AI MUST focus on three exported Keras/TensorFlow artifacts:

- Battery RUL PINN-LSTM hybrid model.
- Cardiac Risk RNN/LSTM model.
- Metabolic Simulation RNN/LSTM model.

Training is performed in Google Colab free tier. Each model MUST export a `.h5` artifact and document dataset source, preprocessing, train/test split, metrics, model version, and limitations. Minimum target metrics are MAE < 30 days for battery RUL and F1 > 0.85 for cardiac risk.

### V. Security, Configuration, And Docker Are Gates

Plaintext production passwords are forbidden. User passwords MUST be hashed with bcrypt. Secrets, database URLs, MQTT broker settings, and API settings MUST be externalized through configuration/environment variables.

All services required for the prototype MUST run through `docker-compose up`. A task is not demo-ready until the compose flow can start MQTT, backend, database, and dashboard-facing services with documented health checks.

## Architecture Constraints

- Edge source is simulated telemetry only; no real ESP32 firmware is implemented in this phase.
- MQTT is the transport between simulators and backend.
- Backend stack is FastAPI + TimescaleDB + MQTT subscriber.
- Dashboard displays real telemetry and predictions by polling every 5 seconds.
- AI training is notebook-driven in Google Colab using TensorFlow/Keras.
- Testing uses 80/20 train/test split for AI experiments.
- Authentication is limited to basic bcrypt cleanup; no OAuth, RBAC redesign, or broad auth platform work.

## Critical Files To Track

The following files and folders are constitution-level implementation targets:

```text
backend/
|-- mqtt_subscriber.py
|-- models/
|   `-- telemetry.py
|-- ml/
|   |-- battery_rul_pinn_lstm.py
|   |-- cardiac_risk_lstm.py
|   `-- metabolic_lstm.py
|-- edge_algorithms/
|   |-- pan_tompkins.py
|   |-- glucose_analyzer.py
|   `-- coulomb_counter.py
`-- config.py

simulators/
`-- battery_degradation.py

notebooks/
|-- 01_battery_dataset_cleaning.ipynb
|-- 02_train_battery_rul.ipynb
|-- 03_train_cardiac_risk.ipynb
`-- 04_train_metabolic.ipynb
```

If existing repository folders use legacy names, implementation plans MUST either map them clearly to these canonical paths or include explicit migration tasks before feature work begins.

## Quality Gates

Before the prototype is accepted:

- Simulators publish telemetry to MQTT.
- Backend subscriber receives MQTT telemetry and persists it to TimescaleDB.
- Edge algorithms detect arrhythmia, hypoglycemia, and low battery within required timing limits.
- Three LSTM-family models are trained/exported as `.h5` files, or missing datasets/artifacts are documented as blockers with replacement interfaces in place.
- `/api/v1/predictions/*` endpoints return structured AI inference responses.
- Dashboard displays telemetry and predictions from backend data with 5-second polling.
- Password handling uses bcrypt with no plaintext production password comparison.
- `docker-compose up` starts the prototype services.

## Governance

This constitution supersedes ad hoc feature requests for the Smart TwinPac prototype. Any task that conflicts with the out-of-scope list MUST be rejected or deferred. Any change that expands scope beyond data pipeline, edge algorithms, dataset preparation, AI training, prediction endpoints, dashboard telemetry display, security cleanup, or docker-compose operation requires an explicit amendment.

Plans and task lists MUST show how work advances in this order:

1. Data pipeline.
2. Edge algorithms.
3. Dataset preparation.
4. AI training/export.
5. Prediction APIs.
6. Dashboard integration.
7. Security and compose validation.

**Version**: 1.0.0 | **Ratified**: 2026-05-24 | **Last Amended**: 2026-05-24
