# TwinPacemaker Project - DATABASE INVENTORY & DETAILED REPORT
**Generated:** 2026-06-06

---

## 📊 EXECUTIVE SUMMARY

Your TwinPacemaker project has a **hybrid database architecture** with multiple database instances:

| Database Type | Location | Status | Purpose |
|---|---|---|---|
| **TimescaleDB** (Primary) | Docker Container `twinpacemaker_db` | Production/Cloud | Time-series telemetry (ECG, Glucose, Battery) |
| **PostgreSQL** | Docker Container `twinpacemaker_db` | Production/Cloud | User management (Doctors, Patients, Admins) |
| **SQLite** (Local Fallback #1) | `d:\Vibe Coding\TwinPacemaker\twinpacemaker.db` | Local | Edge device fallback |
| **SQLite** (Local Fallback #2) | `d:\Vibe Coding\TwinPacemaker\keepbeat_fallback.db` | Local | Mobile app fallback |
| **SQLite** (Cloud Fallback #1) | `d:\Vibe Coding\TwinPacemaker\cloud_server\keepbeat_v2.db` | Cloud fallback | Server-side fallback if PostgreSQL fails |
| **SQLite** (Cloud Fallback #2) | `d:\Vibe Coding\TwinPacemaker\cloud_server\keepbeat_fallback.db` | Cloud fallback | Additional cloud fallback |
| **MQTT Broker** | Docker Container `twinpacemaker_mqtt` | Real-time Messaging | Sensor data streaming |

---

## 🗄️ DATABASE #1: TIMESCALEDB (PRIMARY - TIME-SERIES)

### Location & Configuration
- **Container Name:** `twinpacemaker_db`
- **Image:** `timescale/timescaledb:latest-pg16`
- **Host:** Docker network `twinpacemaker_mqtt` (internal) or `localhost:5433` (external)
- **Database Name:** `twinpacemaker`
- **Credentials:** 
  - User: `postgres`
  - Password: `password`
- **Port:** `5433` (external), `5432` (internal)

### Configuration File
📄 [infrastructure/docker-compose.yml](infrastructure/docker-compose.yml)

### What It Stores (Telemetry Hypertables)

TimescaleDB is optimized for **time-series data** with automatic table partitioning:

#### 1. **ecg_telemetry** (ECG Heart Rate Data)
```sql
CREATE TABLE IF NOT EXISTS ecg_telemetry (
    timestamp TIMESTAMPTZ NOT NULL,
    patient_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    ecg_value FLOAT,
    heart_rate INT,
    PRIMARY KEY (timestamp, patient_id)
);
-- Creates TimescaleDB hypertable for automatic partitioning
SELECT create_hypertable('ecg_telemetry', 'timestamp', if_not_exists => TRUE);
```

#### 2. **glucose_telemetry** (CGM Continuous Glucose Monitoring)
```sql
CREATE TABLE IF NOT EXISTS glucose_telemetry (
    timestamp TIMESTAMPTZ NOT NULL,
    patient_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    glucose_value FLOAT,
    unit TEXT,
    PRIMARY KEY (timestamp, patient_id)
);
SELECT create_hypertable('glucose_telemetry', 'timestamp', if_not_exists => TRUE);
```

#### 3. **battery_telemetry** (Device Battery Status)
```sql
CREATE TABLE IF NOT EXISTS battery_telemetry (
    timestamp TIMESTAMPTZ NOT NULL,
    patient_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    battery_level FLOAT,
    charging_status TEXT,
    PRIMARY KEY (timestamp, patient_id)
);
SELECT create_hypertable('battery_telemetry', 'timestamp', if_not_exists => TRUE);
```

---

## 🗄️ DATABASE #2: POSTGRESQL (USER MANAGEMENT)

### Same as TimescaleDB (Built-in)
PostgreSQL runs as the base layer under TimescaleDB. It stores:

### What It Stores (User & Admin Tables)

#### 1. **doctors** Table
```sql
CREATE TABLE IF NOT EXISTS doctors (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'doctor',
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Sample Record:**
- ID: `doc_sterling_001`
- Name: `Dr. Julian Sterling`
- Email: `julian.sterling@keepbeat.com`
- Password: `password123`
- Status: `active`

#### 2. **admins** Table
```sql
CREATE TABLE IF NOT EXISTS admins (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3. **patients** Table
```sql
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    doctor_id TEXT REFERENCES doctors(id),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    dob TEXT NOT NULL,
    medical_id TEXT NOT NULL,
    affiliation TEXT,
    diagnosis_notes TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 4. **telemetry** Table (Generic Time-Series)
```sql
CREATE TABLE IF NOT EXISTS telemetry (
    time TIMESTAMPTZ NOT NULL,
    patient_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🗄️ DATABASE #3-6: SQLITE LOCAL/FALLBACK DATABASES

### File Locations
```
📂 d:\Vibe Coding\TwinPacemaker\
├── twinpacemaker.db                    [Edge device local store]
├── keepbeat_fallback.db                [Mobile app fallback]
└── 📂 cloud_server\
    ├── keepbeat_v2.db                  [Cloud fallback #1]
    └── keepbeat_fallback.db            [Cloud fallback #2]
```

### Configuration
**Default Path in Code:** `keepbeat_v2.db`
**Connection String:** `sqlite:///keepbeat_v2.db`

### Purpose
- **Edge Device Fallback:** When MQTT or cloud is unavailable, data stored locally
- **Mobile App Local Cache:** Flutter app stores data before sync
- **Cloud Failover:** Server-side SQLite if PostgreSQL/TimescaleDB is down

### SQLite Schema (Mobile App)
📄 [mobile_app/lib/database/local_data_repository.dart](mobile_app/lib/database/local_data_repository.dart)

```sql
CREATE TABLE sensor_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT
);
```

---

## 🌐 MQTT MESSAGE BROKER

### Configuration
- **Container Name:** `twinpacemaker_mqtt`
- **Image:** `eclipse-mosquitto:latest`
- **Ports:**
  - MQTT Protocol: `1883:1883`
  - WebSocket: `9001:9001`
- **Data Storage:** `./mosquitto/data/`
- **Config Location:** `./mosquitto/config/`
- **Logs:** `./mosquitto/log/`

### Purpose
**Real-time sensor data streaming** from devices to backend:
- ECG data (heart rate)
- Glucose readings (CGM)
- Battery status
- Device metrics

### Configuration Files
📄 [mosquitto/config/](mosquitto/config/)

---

## 🔌 DATABASE CONNECTION FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                    EDGE DEVICES / MOBILE                    │
│              (Patient Devices with Sensors)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
              ┌──────┴────────┐
              │ (MQTT Topic)  │
              ▼               ▼
        ┌─────────┐    ┌──────────────┐
        │ ONLINE  │    │ OFFLINE      │
        │         │    │              │
        │ MQTT    │    │ Store Local  │
        │ Broker  │    │ SQLite ─────┐│
        └────┬────┘    └──────────────┘│
             │                         │
             └────────┬────────────────┘
                      │
         ┌────────────▼────────────────┐
         │      Backend API            │
         │   (FastAPI/Python)          │
         │   db_manager.py             │
         └────────────┬────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │ (Fallback Logic)          │
        ▼                           ▼
   ┌─────────────┐          ┌──────────────┐
   │ PostgreSQL  │ FAILS → │ SQLite       │
   │ TimescaleDB │          │ Fallback     │
   │             │          │              │
   │ • ecg_      │          │ keepbeat_v2  │
   │   telemetry │          │ .db          │
   │ • glucose_  │          │              │
   │   telemetry │          └──────────────┘
   │ • battery_  │
   │   telemetry │
   │ • doctors   │
   │ • patients  │
   │ • admins    │
   └─────────────┘
```

---

## 💾 DATABASE INITIALIZATION & SEEDING

### Files Responsible
| File | Purpose |
|------|---------|
| [backend/database.py](backend/database.py) | SQLAlchemy ORM initialization for TimescaleDB |
| [cloud_server/db_manager.py](cloud_server/db_manager.py) | PostgreSQL + SQLite connection management |
| [cloud_server/final_seed.py](cloud_server/final_seed.py) | Seeds test doctor account |
| [cloud_server/seed.py](cloud_server/seed.py) | Initial database setup |
| [fix_db_migration.py](fix_db_migration.py) | Database migration helper |

### How to Initialize
```bash
# In Docker (Automatic)
docker-compose up -d

# Manual seeding
cd cloud_server
python final_seed.py
```

### Test Credentials (Pre-seeded)
- **Doctor Email:** `julian.sterling@keepbeat.com`
- **Password:** `password123`

---

## 📈 DATA FLOW & ARCHITECTURE

### Telemetry Ingestion Path
```
Edge Device (Pacemaker/CGM) 
    ↓ (MQTT)
Mosquitto Broker (mosquitto:1883)
    ↓ (Subscribe)
Backend MQTT Subscriber
    (mqtt_subscriber service in docker-compose.yml)
    ↓
db_manager.py (connect & insert)
    ↓
TimescaleDB (ecg_telemetry, glucose_telemetry, battery_telemetry)
    ↓ (Automatic partitioning by timestamp)
Hypertable Data Chunks (optimized queries)
```

### User Authentication Path
```
Mobile/Web Client
    ↓ (POST /login)
Backend API (FastAPI)
    ↓ (Query)
PostgreSQL (doctors/patients table)
    ↓
Return JWT Token
    ↓
Authorized API Calls
```

---

## 🔧 KEY DATABASE FILES IN PROJECT

### Backend Configuration
📄 [backend/config.py](backend/config.py) - Database URL configuration

### Database Models
📄 [backend/models/telemetry.py](backend/models/telemetry.py) - SQLAlchemy models
📄 [cloud_server/models.py](cloud_server/models.py) - Pydantic schemas

### Backend Services
📄 [backend/main.py](backend/main.py) - FastAPI app entry point
📄 [backend/mqtt_subscriber.py](backend/mqtt_subscriber.py) - MQTT data consumer

---

## 🚀 DOCKER COMPOSE VOLUMES

```yaml
volumes:
  timescaledb_data:  # Persistent PostgreSQL/TimescaleDB data
    # Mounted to: /var/lib/postgresql/data
    # Location on Host: Docker named volume (managed by Docker)
```

**To find actual host location:**
```bash
docker volume inspect twinpacemaker_timescaledb_data
# Returns: /var/lib/docker/volumes/twinpacemaker_timescaledb_data/_data
```

---

## 📋 DATABASE SIZE & PERFORMANCE

### Estimated Data
- **ECG Data:** ~250 samples/min per patient = ~360K/day
- **Glucose Data:** ~5 samples/day per patient = ~1.8K/day  
- **Battery Data:** ~1 sample/min per device = ~1.4K/day
- **Storage Optimization:** TimescaleDB automatic compression = ~90% space savings

### Query Performance
- **Hypertables:** Time-range queries optimized with automatic partitioning
- **Indexes:** `(timestamp, patient_id)` composite index for fast lookups
- **Retention:** No auto-purge configured (configure in TimescaleDB if needed)

---

## ⚠️ CRITICAL ISSUES & RECOMMENDATIONS

### ✅ Current Safeguards
1. **Fallback Strategy** - SQLite backup if PostgreSQL fails
2. **Docker Volumes** - Data persistence across container restarts
3. **Health Checks** - docker-compose has health checks enabled
4. **MQTT Persistence** - Messages can queue if subscriber offline

### ⚠️ Potential Issues to Monitor
1. **Password Hardcoded** - Uses `password` as default (change in production)
2. **No Backup Automation** - Manual backup required for disaster recovery
3. **No Data Encryption** - Consider TLS for PostgreSQL connections
4. **SQLite Limitations** - Not suitable for >1 concurrent writer, max 2GB per DB
5. **No Retention Policy** - Old telemetry data never deleted

### 🔐 Production Recommendations
```bash
# 1. Use environment variables
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# 2. Enable TimescaleDB compression
ALTER TABLE ecg_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp DESC'
);

# 3. Set retention policy (delete data older than 1 year)
SELECT add_retention_policy('ecg_telemetry', INTERVAL '1 year');

# 4. Regular backups
pg_dump twinpacemaker > backup_$(date +%Y%m%d_%H%M%S).sql

# 5. Monitor with pg_stat_statements
CREATE EXTENSION pg_stat_statements;
```

---

## 🎯 SUMMARY TABLE: WHERE IS WHAT?

| Data Category | Storage | Technology | Access Method |
|---|---|---|---|
| Heart Rate (ECG) | `ecg_telemetry` table | TimescaleDB | Real-time MQTT → PostgreSQL |
| Glucose (CGM) | `glucose_telemetry` table | TimescaleDB | Real-time MQTT → PostgreSQL |
| Battery Status | `battery_telemetry` table | TimescaleDB | Real-time MQTT → PostgreSQL |
| Doctor Accounts | `doctors` table | PostgreSQL | API endpoints |
| Patient Records | `patients` table | PostgreSQL | API endpoints |
| Admin Users | `admins` table | PostgreSQL | API endpoints |
| Offline Cache | `.db` files | SQLite | Local storage (fallback) |
| Real-time Messaging | MQTT Topics | Mosquitto | Pub/Sub broker |

---

## 📞 QUICK REFERENCE

### To Connect to Database (Local Machine)
```bash
# TimescaleDB/PostgreSQL
psql -h localhost -p 5433 -U postgres -d twinpacemaker

# SQLite (Cloud fallback)
sqlite3 cloud_server/keepbeat_v2.db

# SQLite (Local edge device)
sqlite3 twinpacemaker.db
```

### To Start Everything
```bash
cd d:\Vibe Coding\TwinPacemaker
docker-compose -f docker-compose.yml up -d
docker-compose -f infrastructure/docker-compose.yml up -d
```

### To Check Container Status
```bash
docker ps | grep twinpacemaker
docker logs twinpacemaker_db
docker logs twinpacemaker_mqtt
```

---

**Report Generated:** 2026-06-06  
**Project:** TwinPacemaker (Smart Cardiac Monitoring System)  
**Scope:** Complete database inventory and architecture documentation
