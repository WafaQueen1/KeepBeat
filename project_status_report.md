# KeepBeat Platform — Unified Project Status Report
*Generated: 2026-06-08*

---

## 🎯 Platform Overview

The **KeepBeat** (formerly TwinPacemaker) platform is a high-fidelity **medical Digital Twin ecosystem** designed to simulate, monitor, and predict the physiological state of a pacemaker patient in real time.

Development has been cleanly separated into two distinct repositories to divide backend infrastructure and mobile application development:

1. **`TwinPacemaker` (Core Infrastructure & AI Backend)**: Houses the Dockerized databases, MQTT brokers, FastAPI backend, and the trained AI models.
2. **`KeepBeat-main` (Mobile App)**: Exclusively houses the Flutter application that acts as the patient-facing Fog Node.

---

## 🏗️ Dual-Repository Architecture

### 1. Core Infrastructure (`d:\Vibe Coding\TwinPacemaker`)
* **Role**: The brain and database of the operation.
* **Infrastructure**: Dockerized (TimescaleDB, Mosquitto MQTT, FastAPI).
* **AI Models**: Contains the actual trained `.keras` neural networks for Cardiac Risk (CNN-LSTM), Battery RUL (PINN-LSTM), and Metabolic/Glucose (Stacked LSTM).
* **Interfaces**: Hosts the Doctor Dashboard and AI Prototyping Console.
* **Network**: Exposes the REST API on `port 8000` for the mobile app to connect to.

### 2. Mobile Client (`d:\Vibe Coding\KeepBeat-main`)
* **Role**: The patient interface.
* **App Code**: Located in `mobile_app/`.
* **Connectivity**: The app points to `http://<your-pc-ip>:8000` (configured in `mobile_app/lib/config/app_config.dart`) to fetch live predictions from the `TwinPacemaker` backend.

---

## 🚀 Current Action Plan

By splitting the responsibilities:
- You don't need to migrate the complex AI models or databases.
- You can leave `TwinPacemaker` running in the background.
- You can focus all your active Flutter UI coding in the `KeepBeat-main` directory.

### ✅ What's Working
* The AI Models in `TwinPacemaker` successfully load and generate predictions via the backend API.
* The Flutter app in `KeepBeat-main` compiles and runs.
* The Flutter app is successfully configured to connect to port 8000 (`TwinPacemaker`'s backend).

### 🔜 Next Steps
* Keep Docker Desktop running to ensure `TwinPacemaker` stays active in the background.
* Continue building and refining the Flutter UI in `KeepBeat-main` to display the real predictions fetched from `TwinPacemaker`.
