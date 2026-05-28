# Smart TwinPac Digital Twin — Project Report

## Executive Summary
The **Smart TwinPac** project is a state-of-the-art Digital Twin ecosystem designed for modern pacemakers and implantable medical devices. It bridges the gap between raw medical telemetry and proactive patient care by combining edge analytics, high-throughput data streaming, and advanced machine learning models. 

This project successfully implements a full end-to-end pipeline: from simulating physiological telemetry to real-time ingestion, database storage, AI-driven predictive modeling, and a real-time web dashboard.

---

## 🏗️ System Architecture

The ecosystem relies on a modern microservices architecture, containerized via Docker for seamless deployment.

- **Data Ingestion (MQTT)**: Eclipse Mosquitto handles high-frequency telemetry streaming (ECG, glucose, battery metrics).
- **Time-Series Database**: TimescaleDB (PostgreSQL) is used to efficiently store and query dense historical telemetry.
- **Backend API**: A highly asynchronous FastAPI backend orchestrates data processing, database operations, and AI inference.
- **Frontend Dashboard**: A lightweight, Vanilla HTML/CSS/JS frontend polls the backend to visualize live telemetry and predictive alerts in real-time.

---

## 🧠 Artificial Intelligence Models

Three independent, highly specialized deep learning models were developed to monitor and predict patient risk across different physiological and hardware domains.

### 1. Battery Remaining Useful Life (PINN-LSTM)
A Physics-Informed Neural Network (PINN) designed to predict when the pacemaker battery will need replacement.
- **Physics Branch**: Learns the physical degradation parameters of the Shepherd battery model.
- **Data-Driven Branch**: An LSTM that captures complex, non-linear temporal degradation patterns over time.
- **Target**: Maintain Mean Absolute Error (MAE) under 30 days for long-term predictability.

### 2. Cardiac Arrhythmia Risk (BiLSTM)
A Bidirectional LSTM trained to detect subtle precursors to critical cardiac events.
- **Input**: 1D ECG waveforms and R-peak metrics.
- **Output**: 24-hour arrhythmia risk probability.
- **Action**: Triggers moderate/critical alerts allowing preemptive clinical intervention before an event occurs.

### 3. Glucose & Metabolic Dynamics (Stacked LSTM)
A metabolic prediction model leveraging the mathematical **Bergman Minimal Model** to simulate glucose-insulin interactions.
- **Architecture**: A dual-input Stacked LSTM (128 → 64 → 32 units).
- **Inputs**: Time-series glucose/insulin history combined with metadata (meals, exercise intensity).
- **Target**: Predicts blood glucose levels 1 hour into the future with high clinical accuracy (MAE < 15 mg/dL), enabling proactive alerts for hypoglycemia and hyperglycemia.

---

## ⚙️ Backend Integration & Security

### Unified AI Inference
The backend features a unified endpoint (`/api/v1/predictions/all/{patient_id}`) that concurrently evaluates all three AI models. It aggregates the inferences and translates them into actionable clinical alerts (e.g., "Battery Replacement URGENT", "Hypoglycemia predicted").

### Security (Zero Plaintext)
- Implemented `bcrypt` for all credential management.
- Hardcoded secret scanners and environment variable validators ensure the system cannot boot with compromised default passwords.

### Smoke Testing
A comprehensive test suite (`scripts/smoke_test.py`) was created to perform end-to-end verification. It validates API health, database writes, MQTT publishing flow, dashboard connectivity, and AI inference logic.

---

## 🖥️ Live Dashboard Interface
The user interface is designed with a premium, medical-grade aesthetic (dark mode, glassmorphism hints, and modern typography). 
- **Live Widgets**: Displays instantaneous Heart Rate with an animated synthetic ECG waveform.
- **Predictive Panels**: Dedicated visual real-estate for the PINN-LSTM battery RUL, BiLSTM Cardiac Risk (with risk gauges), and Glucose trend predictions.
- **Alert Ticker**: A centralized, color-coded notification area that aggregates critical AI warnings.

---

## 🚀 Next Steps & Future Enhancements
1. **Docker Deployment**: Bring up the entire cluster using `docker-compose up --build -d`.
2. **Clinical Validation**: Train the models on larger, real-world clinical datasets (e.g., actual MIMIC-IV data) rather than the current synthetic/simulated data.
3. **Edge Optimization**: Convert the TensorFlow `.keras` models using TensorFlow Lite for direct deployment onto edge devices or smartphone companions.
