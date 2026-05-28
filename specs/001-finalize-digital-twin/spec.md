# Feature Specification: Finalize TwinPacemaker Digital Twin Platform

**Feature Branch**: `001-finalize-digital-twin`  
**Created**: 2026-05-13  
**Status**: Draft  
**Input**: User clarification for TwinPacemaker / KeepBeat finalization, including Chapter 5 alignment requirements.

## User Scenarios & Testing

### User Story 1 - Real-Time Patient Monitoring MVP (Priority: P1)

A patient can open the KeepBeat mobile app and see live cardiac, glucose, battery, and alert state derived from simulator/MQTT/cloud data.

**Why this priority**: This proves the core Physical to Edge to Cloud telemetry loop and gives the project a demonstrable MVP.

**Independent Test**: Start MQTT, backend, simulators, and mobile app; verify changing simulator values appear in the mobile dashboard and trigger local alerts.

**Acceptance Scenarios**:

1. **Given** MQTT and backend services are running, **When** CGM and pacemaker simulators publish telemetry, **Then** the mobile app displays updated values without restarting.
2. **Given** glucose or battery values cross configured safety thresholds, **When** the mobile app receives the reading, **Then** it shows a clear alert and links to the appropriate reactive/recovery plan.
3. **Given** the app is offline or cloud sync fails, **When** telemetry arrives locally, **Then** the edge app stores or displays local readings and reports sync status without crashing.

---

### User Story 2 - Clinician Dashboard Visibility (Priority: P2)

A doctor can log into the dashboard, view assigned patients, inspect recent telemetry, and see risk/diagnostic summaries.

**Why this priority**: The system is a clinical monitoring platform, so clinician review is the second essential demonstration path.

**Independent Test**: With seeded demo data and live telemetry, open the dashboard and verify patient list, telemetry cards, ECG display, and AI diagnostic sections render from API/live data.

**Acceptance Scenarios**:

1. **Given** a doctor account is approved, **When** the doctor logs in, **Then** assigned patients and recent telemetry are available.
2. **Given** telemetry exists for a patient, **When** the dashboard loads, **Then** cardiac, glucose, battery, and alert information appears consistently across dashboard views.
3. **Given** no telemetry is available, **When** the dashboard loads, **Then** it displays a non-crashing empty state.

---

### User Story 3 - Chapter 5 Edge Algorithms (Priority: P3)

The edge/mobile layer performs or hosts clinically relevant preprocessing and rule logic aligned with Chapter 5, including Pan-Tompkins-style ECG feature extraction and multi-threshold glucose classification.

**Why this priority**: These algorithms connect the product to the stated academic/technical claims rather than leaving the UI as a simple telemetry viewer.

**Independent Test**: Feed known ECG/glucose sample sequences into algorithm tests and verify R-peak, heart-rate, glucose state, and alert outputs against expected labels.

**Acceptance Scenarios**:

1. **Given** ECG sample data, **When** the edge algorithm runs, **Then** R-peaks and derived heart-rate features are produced using a documented Pan-Tompkins-compatible pipeline.
2. **Given** glucose sample data, **When** readings cross hypo/normal/hyper thresholds, **Then** multi-threshold glucose state and patient action recommendations are produced.
3. **Given** algorithm input is noisy or incomplete, **When** processing runs, **Then** the app emits a degraded-quality status instead of false certainty.

---

### User Story 4 - Cloud Predictive Models (Priority: P4)

The cloud backend exposes predictive outputs for battery RUL, cardiac risk, and metabolic risk, with model-version metadata and safe fallback behavior.

**Why this priority**: LSTM to PINN Battery RUL, LSTM cardiac risk, and LSTM metabolic risk are core finalization gaps, but they depend on stable ingestion and data contracts first.

**Independent Test**: Submit representative telemetry sequences to backend model endpoints/services and verify deterministic demo predictions, validation metrics, and model metadata are returned.

**Acceptance Scenarios**:

1. **Given** battery telemetry history, **When** RUL inference runs, **Then** the backend returns estimated RUL, confidence/quality metadata, and model version.
2. **Given** cardiac telemetry history, **When** cardiac risk inference runs, **Then** the backend returns a risk class and rationale fields suitable for dashboard display.
3. **Given** metabolic telemetry history, **When** metabolic inference runs, **Then** the backend returns glucose risk classification and recommended monitoring urgency.

---

### User Story 5 - Finalization Quality Gates (Priority: P5)

The project has a reliable setup path, security cleanup, smoke tests, and documentation sufficient for a final demo or handoff.

**Why this priority**: The system currently has hardcoded credentials/hosts, minimal tests, and placeholder docs that can undermine the final presentation.

**Independent Test**: A new developer can follow the quickstart, run tests/builds, and demo the full data flow from a clean checkout.

**Acceptance Scenarios**:

1. **Given** a clean repo checkout, **When** setup instructions are followed, **Then** all required services start in the documented order.
2. **Given** test commands are run, **When** code is healthy, **Then** mobile, backend, and dashboard smoke checks pass.
3. **Given** credentials and endpoints are configured, **When** the app runs outside a local demo, **Then** secrets are not embedded in UI/source defaults.

### Edge Cases

- MQTT broker unavailable or reconnecting.
- Backend unavailable while mobile receives local MQTT telemetry.
- TimescaleDB unavailable and SQLite fallback active.
- Simulator publishes malformed, missing, delayed, or out-of-range data.
- Mixed units for glucose values, especially g/L versus mg/dL.
- ECG samples are noisy, flatline, or too sparse for reliable peak detection.
- Battery level is missing, stuck, or physically impossible.
- Doctor has no assigned patients or pending approval.
- Demo model weights are missing; system must return explicit unavailable status.

## Requirements

### Functional Requirements

- **FR-001**: System MUST maintain a documented end-to-end telemetry path from simulators through MQTT, backend storage, mobile display, and dashboard display.
- **FR-002**: Mobile app MUST display heart/cardiac state, glucose, pacemaker battery, latest alert, and recovery/reactive plan navigation.
- **FR-003**: Mobile edge logic MUST classify glucose using documented multi-threshold states and units.
- **FR-004**: Edge algorithm layer MUST include a testable ECG preprocessing/feature extraction module aligned with Pan-Tompkins concepts.
- **FR-005**: Backend MUST persist telemetry with patient identity, sensor type, timestamp, raw value, processed state, and source metadata.
- **FR-006**: Backend MUST expose telemetry retrieval APIs for mobile/dashboard consumers.
- **FR-007**: Backend MUST provide predictive service interfaces for battery RUL, cardiac risk, and metabolic risk.
- **FR-008**: Battery RUL design MUST support an LSTM baseline and a PINN-enhanced or PINN-compatible path, with documented fallback if trained models are unavailable.
- **FR-009**: Cardiac and metabolic risk design MUST support LSTM-based sequence inference or deterministic demo substitute marked as non-clinical.
- **FR-010**: Dashboard MUST show patient telemetry, ECG visualization, battery/RUL state, and diagnostic summaries from real API or MQTT data where available.
- **FR-011**: System MUST externalize local hostnames, ports, credentials, and API URLs into environment/configuration surfaces.
- **FR-012**: System MUST not store or compare production passwords in plaintext.
- **FR-013**: System MUST include smoke/integration tests for telemetry ingestion, mobile analyzer/build health, backend API health, and dashboard build health.
- **FR-014**: Documentation MUST include startup order, ports, demo credentials, safety disclaimers, troubleshooting, and validation commands.
- **FR-015**: All AI/algorithm outputs MUST be labeled as demo/research support unless validated clinical models and datasets are supplied.

### Key Entities

- **Patient**: Person monitored by the platform; includes identity, doctor assignment, approval state, and clinical telemetry linkage.
- **Doctor**: Clinician user who can review assigned patients and telemetry.
- **TelemetryReading**: Timestamped value from pacemaker, CGM, ECG, battery, or derived signal.
- **AlertEvent**: Threshold or model-triggered event with severity, cause, recommendation, and acknowledgment state.
- **EdgeAnalysisResult**: Local processed output such as ECG features, glucose classification, and sync status.
- **ModelPrediction**: Cloud AI output with prediction type, value/class, confidence/quality fields, model version, and input window metadata.
- **DeviceState**: Pacemaker/CGM connectivity, battery, and simulator/source metadata.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Full demo data flow from simulators to mobile and dashboard completes in under 10 minutes from documented startup.
- **SC-002**: Mobile analyzer reports zero errors for application code.
- **SC-003**: Dashboard production build completes successfully.
- **SC-004**: Backend health/import smoke test completes successfully against configured dependencies or documented fallback.
- **SC-005**: At least one automated or scripted test validates each of glucose thresholding, telemetry ingestion, and model service fallback behavior.
- **SC-006**: Documentation identifies every demo-only clinical/AI claim and avoids presenting unvalidated predictions as medical decisions.

## Assumptions

- The current repo is the baseline implementation and will be finalized rather than rewritten.
- Chapter 5 details are authoritative for algorithm names, expected modules, and validation direction.
- If trained LSTM/PINN model files or datasets are not available, deterministic demo services will be implemented with clear labels and interfaces ready for model replacement.
- The first finalization target is a reliable local demo, not regulated production deployment.
- TimescaleDB is preferred for full flow, with SQLite fallback retained for local resilience.
