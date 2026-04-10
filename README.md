# TwinPacemaker: The Digital Twin Clinical Platform

TwinPacemaker is a high-fidelity, end-to-end medical monitoring ecosystem that synchronizes real-time cardiac and metabolic data across a hybrid fog-to-cloud architecture. It features a "Digital Twin" simulation of patient vitals (CGM and Pacemaker) integrated with a clinician-facing governance dashboard.

---

## 🏗️ System Architecture

TwinPacemaker follows a four-layer architecture:

1. **Simulation Layer** (`/device_simulators`): Python-based modules that generate real-time heart rate (BPM) and glucose (g/L) data, streaming via MQTT.
2. **Infrastructure Layer** (`/infrastructure`): Containerized services including **TimescaleDB** (PostgreSQL-based time-series DB) and **Mosquitto MQTT** (Broker for low-latency transmission).
3. **Cloud Layer** (`/cloud_server`): FastAPI backend (Python) managing identity, administrative approvals, and time-series data ingestion into TimescaleDB.
4. **Interface Layer**:
   - **Mobile App** (`/mobile_app`): Flutter-based "Fog Node" for patients, providing local telemetry and real-time clinical alerts.
   - **Doctor Dashboard** (`/doctor_dashboard`): Vite-based clinical control center for medical specialists to monitor patient outcomes.

---

## ⚙️ Technical Configuration

### Core Ports & Services
| Service | Port (Host) | Description |
| :--- | :--- | :--- |
| **Mosquitto MQTT** | `1883` | TCP Broker |
| **Mosquitto Web** | `9001` | WebSocket (for Flutter Web) |
| **TimescaleDB** | `5433` | Time-series Database (Postgres) |
| **Cloud API** | `8000` | FastAPI Backend |
| **Dashboard** | `5173` | Vite Dev Server |

### Initial Credentials (Seeded)
- **Doctor**: `julian.sterling@keepbeat.com` / `password123`
- **Admin**: `admin@keepbeat.com` / `admin123`

---

## 🚀 Setup & Execution

### 1. Infrastructure
Ensure Docker is running and launch the core services:
```ps1
cd infrastructure
docker-compose up -d
```

### 2. Backend & Simulators
The backend utilizes a Python virtual environment for dependency isolation.
```ps1
cd cloud_server
# Launch API
.\venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000
```
Start the simulators from the root:
```ps1
.\cloud_server\venv\Scripts\python .\device_simulators\pacemaker_sensing_module.py
.\cloud_server\venv\Scripts\python .\device_simulators\cgm_sensing_module.py
```

### 3. Interface Launch
**Mobile App (Web Version)**:
```ps1
cd mobile_app
flutter run -d chrome
```

**Doctor Dashboard**:
```ps1
cd doctor_dashboard
npm install
npm run dev
```

---

## 🛡️ Clean Code & Design Principles
- **Aesthetics**: Follows the "Vital Pulse" Stitch Design System (Claymorphism, Bento-box grids).
- **Architecture**: Enforces a strict separation of concerns between ingestion, persistence, and presentation.
- **Consistency**: Uses a centralized `AppTheme` and common provider-based state management in Flutter.
