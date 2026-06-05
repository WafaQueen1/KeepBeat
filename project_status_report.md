# TwinPacemaker — Project Status Report
*Generated: 2026-06-05*

---

## 🎯 What Is TwinPacemaker?

**TwinPacemaker** is a high-fidelity **medical Digital Twin platform** — a full-stack clinical ecosystem that simulates, monitors, and predicts the physiological state of a pacemaker patient in real time.

Think of it as three things in one:
1. A **real-time medical IoT pipeline** — device sensors → MQTT → database
2. A **clinical AI engine** — three trained neural networks predicting cardiac risk, battery life, and glucose
3. A **multi-interface clinical portal** — doctor dashboard, mobile patient app, and a direct AI prototyping console

The platform is called **KeepBeat** (brand name), built on a **Smart TwinPac** backend.

---

## 🏗️ System Architecture Overview

```
[Hardware: ESP32 + AD8232 ECG Sensor]
         |
   Bluetooth Serial
         |
  [local_bluetooth_relay.py]  ←  Local Python bridge
         |
   HTTP POST via Internet
         |
  [FastAPI Cloud Backend]  ←  Docker container on port 8000
     |          |         |
     |          |         └── POST /api/model/cardiac/predict
     |          |              POST /api/model/battery/predict
     |          |              POST /api/model/metabolic/predict
     |          |              WS  /ws/ecg  (live streaming)
     |          |
     |    [TimescaleDB]   ←  Time-series PostgreSQL
     |          |
  [MQTT Broker] ←  Mosquitto (pacemaker + CGM simulators)
     |
     └── [Device Simulators] (Python scripts)
           ├── pacemaker_sensing_module.py
           └── cgm_sensing_module.py
```

```
[Interfaces]
├── frontend/dashboard.html         ←  Static clinical monitoring dashboard
├── frontend/model-prototype.html   ←  🔬 AI Prototyping Console (3 models)
├── doctor_dashboard/               ←  Vite React app for doctors
└── mobile_app/                     ←  Flutter patient app (fog node)
```

---

## 🤖 Trained AI Models

Three neural networks were trained in Jupyter notebooks and live in `models/`:

| Model | File | Architecture | Task | Test Performance |
|---|---|---|---|---|
| **Cardiac CNN-LSTM** | `models/cardiac/cardiac2/best_model_cnn_lstm.keras` | CNN + LSTM | ECG arrhythmia classification (binary or 4-class) | ~99.4% val accuracy |
| **Battery PINN-LSTM** | `models/battery/battery_pinn_lstm.keras` | Physics-Informed LSTM | Remaining Useful Life (days) | MAE: 8.5 cycles, R²: 0.89 |
| **Metabolic Stacked LSTM** | `models/metabolic_stacked_lstm_best.keras` | 3-layer LSTM + Dense | Glucose level 60 min ahead (mg/dL) | MAE: 13.7 mg/dL |

All three models are now exposed via REST API and callable from the AI Prototyping Console.

---

## 🐳 Running Infrastructure (Docker)

Four Docker containers defined in `docker-compose.yml`:

| Container | Role | Status |
|---|---|---|
| `twinpac_timescaledb` | TimescaleDB (time-series data) | ✅ Running |
| `twinpac_mqtt` | Mosquitto MQTT broker | ✅ Running |
| `twinpac_backend` | FastAPI backend + AI models | ⚠️ **Currently broken** (see below) |
| `twinpac_mqtt_subscriber` | Python bridge from MQTT → DB | ⚠️ Depends on backend |

---

## ⚠️ Current Active Problem

**The backend container is crashing on startup** with:
```
ModuleNotFoundError: No module named 'tensorflow'
```

**Root cause:** TensorFlow was not in `backend/requirements.txt`, so the Docker image was being built without it. The backend services (`battery_prediction_service.py`, `cardiac_prediction_service.py`, `metabolic_prediction_service.py`) all import TensorFlow at the top level, which crashes the entire FastAPI app before it can serve any routes — this is why you see **404 errors for every endpoint**.

**Fix applied (awaiting rebuild):**
- Added `tensorflow>=2.15.0` to [requirements.txt](file:///d:/Vibe%20Coding/TwinPacemaker/backend/requirements.txt)
- Triggered `docker-compose up --build -d` — the build completed, but the container may still be starting due to TensorFlow's large install size.

> [!IMPORTANT]
> TensorFlow is ~600MB so the Docker rebuild is slow (can take 5-10 minutes to fully install inside the container). Once it completes successfully, ALL three prediction endpoints will come alive automatically.

---

## 🔬 AI Prototyping Console — What Was Built

The [model-prototype.html](file:///d:/Vibe%20Coding/TwinPacemaker/frontend/model-prototype.html) is the central test bed. It was recently expanded to host **all three model UIs** in one page:

### 1. Cardiac Risk (CNN-LSTM)
- Input: Raw 187-sample ECG sequence (comma-separated)
- Auto-streams from WebSocket (`ws://localhost:8000/ws/ecg`) if ESP32 hardware is connected
- Output: Risk level (low/moderate/high) + risk probability %

### 2. Battery RUL (PINN-LSTM)
- Input: 30 timesteps × 4 features [Voltage, Current, Capacity, Temperature]
- "Auto-fill Dummy Data" button generates a realistic degrading battery sequence in correct JSON format
- Output: Remaining Useful Life in days + confidence %

### 3. Metabolic/CGM (Stacked LSTM)
- Input: 12 historical glucose readings (5-min intervals, 60 min window) + 5 metadata values [CHO, insulin, Risk, LBGI, HBGI]
- "Auto-fill Dummy Data" button for quick testing
- Output: Predicted glucose in 60 minutes + risk classification (normal / hypo / hyper risk)

---

## 📁 Key Files Reference

| File | Purpose |
|---|---|
| [backend/main.py](file:///d:/Vibe%20Coding/TwinPacemaker/backend/main.py) | FastAPI app — all API routes |
| [backend/requirements.txt](file:///d:/Vibe%20Coding/TwinPacemaker/backend/requirements.txt) | Python dependencies for Docker |
| [backend/Dockerfile](file:///d:/Vibe%20Coding/TwinPacemaker/backend/Dockerfile) | Docker image build config |
| [backend/services/cardiac_prediction_service.py](file:///d:/Vibe%20Coding/TwinPacemaker/backend/services/cardiac_prediction_service.py) | Cardiac CNN-LSTM inference |
| [backend/services/battery_prediction_service.py](file:///d:/Vibe%20Coding/TwinPacemaker/backend/services/battery_prediction_service.py) | Battery PINN-LSTM inference |
| [backend/services/metabolic_prediction_service.py](file:///d:/Vibe%20Coding/TwinPacemaker/backend/services/metabolic_prediction_service.py) | Metabolic LSTM inference |
| [frontend/model-prototype.html](file:///d:/Vibe%20Coding/TwinPacemaker/frontend/model-prototype.html) | AI Prototyping Console (all 3 models) |
| [frontend/dashboard.html](file:///d:/Vibe%20Coding/TwinPacemaker/frontend/dashboard.html) | Clinical monitoring dashboard |

---

## ✅ What's Working / ❌ What's Not

| Feature | Status |
|---|---|
| Docker infrastructure (DB, MQTT) | ✅ Running |
| TimescaleDB schema + data ingestion | ✅ Working |
| Device simulators (pacemaker + CGM) | ✅ Working |
| Doctor Dashboard (Vite app) | ✅ Working |
| FastAPI backend serving routes | ❌ Crashing (TensorFlow missing — fix applied, rebuilding) |
| `/api/model/cardiac/predict` endpoint | ❌ 404 (backend down) |
| `/api/model/battery/predict` endpoint | ❌ 404 (backend down) |
| `/api/model/metabolic/predict` endpoint | ❌ 404 (backend down) |
| AI Prototyping Console HTML/JS | ✅ UI is correct, waiting for backend |
| WebSocket ECG streaming | ❌ Disconnected (backend down) |

---

## 🔜 Next Steps (After Docker Rebuild Succeeds)

1. **Verify all 3 AI endpoints** work via the prototyping console
2. **Test with real ECG data** from the ESP32 Bluetooth relay
3. **Refine model outputs** — the cardiac CNN-LSTM was trained on a public MIT-BIH dataset and may need output mapping to match the exact label schema
4. **Connect doctor_dashboard** to use the new AI prediction endpoints for live alerts
5. **Mobile app** — connect the Flutter fog node to the IoT pipeline

---

> [!TIP]
> **To check if the backend is now healthy:** Run `docker logs twinpac_backend` in your terminal. If you see `Uvicorn running on http://0.0.0.0:8000`, everything is working. If still showing a TensorFlow error, the build may still be in progress.
