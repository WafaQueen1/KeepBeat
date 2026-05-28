# Research: Finalize TwinPacemaker Digital Twin Platform

## Decisions

### D1: Finalization targets a local demo first

**Decision**: Treat the next milestone as a reliable local research/demo system, not a regulated production medical device.

**Rationale**: Current code contains hardcoded demo credentials, placeholder AI claims, and limited tests. A demo-first scope allows safe labeling while still aligning with Chapter 5.

**Alternatives considered**:

- Production hardening immediately: rejected because clinical validation, security certification, and deployment requirements are outside current repo state.

### D2: Keep existing hierarchical architecture

**Decision**: Preserve Physical/Simulator to Edge/Flutter to Cloud/FastAPI to Dashboard layers.

**Rationale**: This directly matches the user-provided Chapter 5 framing and the existing repository layout.

### D3: Normalize glucose units before algorithm work

**Decision**: Add explicit unit metadata and conversion handling for glucose readings.

**Rationale**: Simulators appear to publish g/L-style values while mobile UI logic checks mg/dL thresholds in places. This can cause false alert behavior.

### D4: Implement algorithm contracts before full trained models

**Decision**: Create service/module interfaces for Pan-Tompkins, Battery RUL, cardiac risk, and metabolic risk, with deterministic demo fallbacks where trained artifacts are missing.

**Rationale**: Chapter 5 alignment requires those named algorithms to exist as testable modules. If model weights/datasets are unavailable, honest fallback behavior is better than hardcoded UI claims.

### D5: Security cleanup is mandatory before final handoff

**Decision**: Externalize credentials/hosts and replace plaintext password comparison for non-demo mode.

**Rationale**: Current repo includes seeded passwords and direct password comparisons. This is acceptable only as clearly documented local demo scaffolding.

## Open Questions

- Where is the authoritative Chapter 5 document or dataset source?
- Are trained LSTM/PINN model files available, or should the project deliver model-ready interfaces only?
- Should ECG Pan-Tompkins processing run inside Flutter edge code, cloud backend, or both for comparison?
- What final demo target is required: Flutter web, Android emulator, Windows desktop, or physical mobile device?
