# Tasks: Smart TwinPac Digital Twin Prototype

**Input**: Constitution priorities and design documents from `/specs/001-finalize-digital-twin/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`  
**Scope Order**: data pipeline -> edge algorithms -> dataset preparation -> AI training  
**Out of Scope**: chatbot/NLP, real ESP32 firmware, mobile app UI redesign, authentication beyond basic bcrypt

## Phase 1: Setup And Canonical Structure

**Purpose**: Prepare the repository for the constitution-defined backend, simulator, and notebook work.

- [ ] T001 Confirm whether existing `cloud_server/` will be migrated to canonical `backend/` or mapped as the backend implementation in `specs/001-finalize-digital-twin/plan.md`.
- [ ] T002 Create or normalize backend package structure for `backend/models/`, `backend/ml/`, `backend/edge_algorithms/`, and `backend/config.py`.
- [ ] T003 Create `notebooks/` folder for Colab training notebooks and add a short README describing Google Colab free-tier execution.
- [ ] T004 Create `simulators/` folder or map existing simulator modules to the canonical simulator path.
- [ ] T005 Add `.env.example` entries for MQTT broker, TimescaleDB URL, API host/port, bcrypt settings, and model artifact paths.

---

## Phase 2: Foundational Data Pipeline

**Purpose**: Establish simulator -> MQTT -> backend -> TimescaleDB flow before algorithms or AI.

- [x] T006 Define telemetry schema in `backend/models/telemetry.py` with patient ID, sensor type, timestamp, value, unit, source, and processing status.
- [x] T007 Add telemetry ingestion endpoint in `backend/models/telemetry.py` or backend router for POST telemetry validation.
- [x] T008 Implement MQTT subscriber skeleton in `backend/mqtt_subscriber.py` with topic subscriptions for ECG, glucose, and battery telemetry.
- [x] T009 Add TimescaleDB connection/configuration in `backend/config.py` using environment variables only.
- [x] T010 Create TimescaleDB hypertable migration or startup initialization for telemetry readings.
- [x] T011 Wire MQTT subscriber to validate telemetry payloads and persist accepted readings into TimescaleDB.
- [ ] T012 Add simulator payload contracts for ECG, glucose, and battery topics in `specs/001-finalize-digital-twin/contracts/`.
- [ ] T013 Fix `simulators/battery_degradation.py` so the battery curve is discharge-only and cannot increase SoC during a run.
- [x] T014 Add a pipeline smoke script or test proving one simulator reading reaches TimescaleDB through MQTT and backend.

**Checkpoint**: Acceptance Criterion 1 is demonstrable: simulators -> MQTT -> backend -> TimescaleDB data flowing.

---

## Phase 3: Edge Algorithms

**Purpose**: Implement deterministic edge analysis before cloud AI.

- [x] T015 Implement Pan-Tompkins-style preprocessing in `backend/edge_algorithms/pan_tompkins.py` for filtering, derivative/squaring, moving integration, R-peak detection, and heart-rate extraction.
- [x] T016 Add arrhythmia decision logic in `backend/edge_algorithms/pan_tompkins.py` for tachycardia, bradycardia, irregular rhythm, and flatline/no-signal conditions.
- [x] T017 Add timing test or benchmark verifying arrhythmia analysis completes in less than 1 second for the target sample window.
- [x] T018 Implement 3-level glucose threshold classification in `backend/edge_algorithms/glucose_analyzer.py` for hypo, normal, and hyperglycemia.
- [x] T019 Add persistence rules in `backend/edge_algorithms/glucose_analyzer.py` to avoid single-sample false alerts and verify hypoglycemia detection in less than 2 seconds.
- [x] T020 Implement Coulomb-counting SoC estimation in `backend/edge_algorithms/coulomb_counter.py` with low battery alert below 20 percent SoC.
- [x] T021 Add unit tests for ECG arrhythmia, glucose threshold/persistence, and battery SoC edge cases.
- [x] T022 Integrate edge algorithm outputs into backend telemetry processing so derived alerts are stored with telemetry metadata.

**Checkpoint**: Acceptance Criterion 2 is demonstrable: arrhythmia <1s, hypoglycemia <2s, battery <20 percent SoC.

---

## Phase 4: Dataset Preparation

**Purpose**: Prepare reproducible datasets for the three required LSTM-family models.

- [x] T023 Create `notebooks/01_battery_dataset_cleaning.ipynb` to transform NASA battery data into pacemaker-style discharge/RUL windows.
- [x] T024 Document battery dataset columns, resampling, normalization, RUL label generation, and 80/20 train/test split inside the notebook.
- [ ] T025 Prepare cardiac sequence dataset pipeline for `notebooks/03_train_cardiac_risk.ipynb` with labels suitable for F1 scoring.
- [x] T026 Prepare metabolic sequence dataset pipeline for `notebooks/04_train_metabolic.ipynb` with glucose trend windows and simulation labels.
- [ ] T027 Export cleaned dataset metadata files documenting sources, split strategy, feature columns, labels, and known limitations.
- [x] T028 Add a dataset blocker note where real datasets are unavailable, including the expected replacement file format.

**Checkpoint**: Training notebooks have defined inputs and reproducible 80/20 split logic.

---

## Phase 5: AI Training And Model Export

**Purpose**: Train/export three `.h5` cloud AI artifacts with documented metrics.

- [x] T029 Implement PINN-LSTM hybrid training script in `backend/ml/battery_rul_pinn_lstm.py`.
- [x] T030 Create `notebooks/02_train_battery_rul.ipynb` that trains Battery RUL PINN-LSTM and targets MAE < 30 days.
- [ ] T031 Export Battery RUL model artifact as `.h5` and write metrics/model card documentation.
- [ ] T032 Implement Bidirectional LSTM training script in `backend/ml/cardiac_risk_lstm.py`.
- [ ] T033 Create `notebooks/03_train_cardiac_risk.ipynb` that trains Cardiac Risk LSTM and targets F1 > 0.85.
- [ ] T034 Export Cardiac Risk model artifact as `.h5` and write metrics/model card documentation.
- [x] T035 Implement Stacked LSTM training script in `backend/ml/metabolic_lstm.py`.
- [x] T036 Create `notebooks/04_train_metabolic.ipynb` that trains Metabolic Simulation LSTM with documented evaluation metrics.
- [ ] T037 Export Metabolic Simulation model artifact as `.h5` and write metrics/model card documentation.

**Checkpoint**: Acceptance Criterion 3 is demonstrable or blockers are documented with model interfaces ready.

---

## Phase 6: Prediction API Integration

**Purpose**: Serve AI inference through backend endpoints.

- [ ] T038 Define prediction request/response schemas for battery RUL, cardiac risk, and metabolic simulation.
- [ ] T039 Implement `/api/v1/predictions/battery-rul` endpoint loading the Battery RUL `.h5` artifact or returning explicit model-unavailable status.
- [ ] T040 Implement `/api/v1/predictions/cardiac-risk` endpoint loading the Cardiac Risk `.h5` artifact or returning explicit model-unavailable status.
- [ ] T041 Implement `/api/v1/predictions/metabolic` endpoint loading the Metabolic Simulation `.h5` artifact or returning explicit model-unavailable status.
- [ ] T042 Add inference metadata to all prediction responses: model name, version, input window, confidence/quality field, and limitations.
- [ ] T043 Add contract/smoke tests for `/api/v1/predictions/*` endpoints.

**Checkpoint**: Acceptance Criterion 4 is demonstrable.

---

## Phase 7: Dashboard, Security, And Compose Validation

**Purpose**: Connect the visible demo and close required gates without widening scope.

- [ ] T044 Connect dashboard telemetry cards to backend telemetry APIs and poll every 5 seconds.
- [ ] T045 Connect dashboard prediction panels to `/api/v1/predictions/*` responses.
- [ ] T046 Add dashboard empty/error/model-unavailable states without redesigning the mobile app UI.
- [ ] T047 Replace plaintext password comparison/storage with bcrypt hashing for backend authentication.
- [ ] T048 Remove hardcoded production-like credentials from source and document demo credentials only in safe setup docs.
- [x] T049 Update `docker-compose.yml` so MQTT, TimescaleDB, backend subscriber/API, and dashboard-facing services start with `docker-compose up`.
- [x] T050 Add final end-to-end verification checklist for all acceptance criteria in `specs/001-finalize-digital-twin/quickstart.md`.

**Checkpoint**: Acceptance Criteria 5, 6, and 7 are demonstrable.

---

## Dependencies & Execution Order

- Phase 1 blocks all implementation because paths and environment configuration must be clear.
- Phase 2 blocks edge algorithms, AI endpoints, and dashboard integration because real telemetry flow is the base of the prototype.
- Phase 3 depends on validated telemetry schemas and can run before cloud model training.
- Phase 4 depends on the algorithm/data contract decisions and prepares Colab work.
- Phase 5 depends on Phase 4 dataset preparation.
- Phase 6 depends on model artifact paths from Phase 5, but endpoints may first return explicit model-unavailable status.
- Phase 7 depends on backend APIs and closes the visible demo/security/compose gates.

## Parallel Opportunities

- T002, T003, and T004 can run in parallel after T001.
- T006, T008, T009, and T012 can run in parallel once backend pathing is settled.
- T015, T018, and T020 can run in parallel because they touch separate edge algorithm files.
- T023, T025, and T026 can run in parallel because they prepare separate datasets.
- T029, T032, and T035 can run in parallel after dataset contracts are fixed.
- T039, T040, and T041 can run in parallel after prediction schemas are defined.

## MVP Recommendation

Complete T001 through T022 first. This proves the core prototype claim: simulated Physical Twin telemetry flows through MQTT/backend/TimescaleDB and deterministic Edge Twin algorithms detect urgent states before any cloud AI claims are added.
