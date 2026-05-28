# Implementation Plan: Finalize TwinPacemaker Digital Twin Platform

**Branch**: `001-finalize-digital-twin` | **Date**: 2026-05-13 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-finalize-digital-twin/spec.md`

## Summary

Finalize the existing TwinPacemaker / KeepBeat platform into a demonstrable hierarchical digital twin: simulators publish pacemaker/CGM telemetry, the edge Flutter app performs local monitoring and Chapter 5 preprocessing, FastAPI persists and serves telemetry, cloud prediction services expose Battery RUL/cardiac/metabolic risk outputs, and the doctor dashboard presents patient status and diagnostics.

The work is incremental: first make the existing code build and run, then validate telemetry flow, then add algorithm/model contracts, then harden security, tests, and documentation.

## Technical Context

**Language/Version**: Dart SDK >=3.3, Flutter; Python FastAPI stack; JavaScript ES modules via Vite.  
**Primary Dependencies**: Flutter Riverpod, mqtt_client, sqflite, http; FastAPI, asyncpg, aiosqlite, Pydantic; Vite, mqtt, Three.js; Mosquitto, TimescaleDB.  
**Storage**: TimescaleDB/PostgreSQL primary, SQLite fallback/local stores.  
**Testing**: Flutter analyzer/widget tests; Python pytest or smoke scripts; Vite build; integration scripts for MQTT/backend flow.  
**Target Platform**: Local demo on Windows/developer workstation, with Docker services for MQTT and DB; Flutter mobile/web target.  
**Project Type**: Multi-component medical monitoring demo: mobile app + API + web dashboard + simulators + infrastructure.  
**Performance Goals**: Near-real-time local telemetry updates; dashboard/mobile refresh within a few seconds of simulator publication in local demo.  
**Constraints**: Must label unvalidated AI outputs as demo/research support; must tolerate MQTT/backend/DB outages; must externalize secrets/endpoints.  
**Scale/Scope**: Single-patient/small-demo scope first, with structure ready for multiple patients/doctors.

## Constitution Check

The current constitution file is still a template, so no enforceable project-specific gates exist yet. This plan establishes temporary finalization gates until the constitution is completed:

- Safety Gate: AI and alert outputs must not be represented as validated clinical decisions.
- Build Gate: mobile analyzer, dashboard build, and backend import/health smoke checks must pass before final demo.
- Data Gate: telemetry units and thresholds must be explicit, especially glucose g/L versus mg/dL.
- Security Gate: production-like flows cannot depend on plaintext hardcoded credentials.
- Observability Gate: startup and runtime failures must produce actionable logs or UI states.

## Project Structure

### Documentation

```text
specs/001-finalize-digital-twin/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
`-- tasks.md
```

### Source Code

```text
cloud_server/
|-- main.py
|-- db_manager.py
|-- models.py
|-- requirements.txt
`-- proposed: services/, tests/

device_simulators/
|-- pacemaker_sensing_module.py
`-- cgm_sensing_module.py

doctor_dashboard/
|-- index.html
|-- main.js
|-- navigation.js
|-- login.html
|-- admin.html
|-- patients.html
|-- ai-diagnostics.html
|-- package.json
`-- proposed: src/config.js or shared config module

infrastructure/
|-- docker-compose.yml
`-- mosquitto/

mobile_app/
|-- lib/
|   |-- main.dart
|   |-- services/
|   |-- providers/
|   |-- database/
|   |-- theme/
|   `-- ui/
|-- test/
|-- pubspec.yaml
`-- proposed: lib/algorithms/, lib/config/, more tests
```

**Structure Decision**: Keep the existing multi-component repo. Add narrow algorithm/config/test modules inside current component directories rather than introducing a new monorepo framework.

## Phase 0: Research

Deliverable: `research.md`

- Confirm Chapter 5 algorithm expectations and translate them into demo-safe implementation boundaries.
- Decide exact glucose units and threshold conversions across simulators, backend, mobile, and dashboard.
- Decide whether Pan-Tompkins runs in Flutter edge code, backend, or both for demo.
- Decide model fallback strategy if trained LSTM/PINN artifacts are unavailable.
- Decide security posture for demo credentials versus production credentials.

## Phase 1: Design

Deliverables: `data-model.md`, `contracts/`, `quickstart.md`

- Define telemetry, alert, edge analysis, and prediction schemas.
- Define API contracts for telemetry ingestion/retrieval and prediction outputs.
- Define MQTT topics/payloads for CGM, pacemaker battery, ECG, and derived alert events.
- Define setup and verification commands.

## Phase 2: Implementation

### Foundation

- Fix current parser/analyzer/build errors.
- Create environment/config modules for hostnames, ports, API URLs, MQTT broker, and demo credentials.
- Normalize telemetry schema and units.
- Add baseline health/smoke commands for each component.

### MVP Data Flow

- Verify simulators publish expected payloads.
- Verify mobile MQTT ingestion and local alerting.
- Verify backend telemetry ingest/retrieval.
- Verify dashboard displays API/live data instead of static placeholders where possible.

### Chapter 5 Algorithms

- Add testable edge algorithm module for glucose thresholding.
- Add Pan-Tompkins-compatible ECG preprocessing module or documented demo subset.
- Add cloud prediction service interfaces:
  - Battery RUL: LSTM baseline with PINN-compatible extension point.
  - Cardiac risk: sequence model interface with deterministic fallback.
  - Metabolic risk: sequence model interface with deterministic fallback.
- Attach model metadata and validation fields to responses.

### Hardening

- Replace plaintext password comparison with hashed-password path for non-demo mode.
- Keep demo seed credentials documented but isolated.
- Add graceful offline/fallback states.
- Update README and mobile README.

## Complexity Tracking

| Concern | Why Needed | Simpler Alternative Rejected Because |
|---------|------------|--------------------------------------|
| Multi-component repo | Existing implementation spans mobile, API, dashboard, simulators, and infra | Rewriting into one app would lose the required hierarchical digital twin architecture |
| Model-service interfaces before real model training | Trained model artifacts/datasets are not confirmed present | Hardcoding UI claims would not satisfy Chapter 5 alignment or future replacement |
| SQLite fallback plus TimescaleDB | Existing code already supports fallback and demo resilience benefits from it | Timescale-only would make local demo fragile when Docker/DB is unavailable |

## Validation Gates

- `flutter analyze` in `mobile_app` has no errors.
- `flutter test` in `mobile_app` passes or documented failing gaps are converted to tasks.
- `npm run build` in `doctor_dashboard` passes.
- Backend imports and health endpoint respond under configured environment.
- MQTT simulators can publish at least CGM and pacemaker battery payloads.
- One documented manual E2E pass proves simulator to UI flow.
