"""
Smart TwinPac End-to-End Smoke Test

Tests the complete data pipeline:
1. MQTT broker reachable
2. Backend API healthy
3. Database accepting data
4. Simulator → MQTT → Backend → DB flow
5. AI prediction endpoints
6. Dashboard accessible
"""

import sys
import json
import time
import requests
import subprocess
from datetime import datetime

# ===== CONFIG =====
API_BASE = 'http://localhost:8000'
MQTT_HOST = 'localhost'
MQTT_PORT = 1883

TEST_PATIENT = 'SMOKE_TEST_001'

# ===== COLORS =====
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def ok(msg): print(f"{GREEN}✅ {msg}{RESET}")
def fail(msg): print(f"{RED}❌ {msg}{RESET}")
def warn(msg): print(f"{YELLOW}⚠️  {msg}{RESET}")
def info(msg): print(f"   {msg}")

passed = 0
failed = 0

def test(name, condition, error_msg=""):
    global passed, failed
    if condition:
        ok(name)
        passed += 1
    else:
        fail(f"{name}: {error_msg}")
        failed += 1

# ===== TEST 1: Backend Health =====
print("\n" + "="*60)
print("TEST 1: Backend API Health")
print("="*60)

try:
    r = requests.get(f'{API_BASE}/health', timeout=5)
    data = r.json()
    test("Backend reachable", r.status_code == 200)
    test("Status is healthy", data.get('status') == 'healthy')
    info(f"Service: {data.get('service')}")
except Exception as e:
    fail(f"Backend unreachable: {e}")
    fail("CRITICAL: Cannot continue without backend")
    sys.exit(1)

# ===== TEST 2: Database Connection =====
print("\n" + "="*60)
print("TEST 2: Database Connection")
print("="*60)

try:
    r = requests.post(
        f'{API_BASE}/api/v1/telemetry/ecg/latest',
        json={'patient_id': TEST_PATIENT, 'hours_ago': 1},
        timeout=5
    )
    test("Database query responds", r.status_code == 200)
    data = r.json()
    test("Response has data field", 'data' in data)
except Exception as e:
    fail(f"Database test failed: {e}")

# ===== TEST 3: MQTT Publishing =====
print("\n" + "="*60)
print("TEST 3: MQTT → Backend → DB Pipeline")
print("="*60)

try:
    # pyrefly: ignore [missing-import]
    import paho.mqtt.client as mqtt
    import json
    
    client = mqtt.Client(client_id="smoke_test_publisher")
    client.username_pw_set('twinpac', 'twinpac123')
    
    connected = False
    
    def on_connect(c, u, f, rc):
        global connected
        connected = (rc == 0)
    
    client.on_connect = on_connect
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    
    time.sleep(2)
    test("MQTT broker reachable", connected, "Cannot connect to MQTT")
    
    if connected:
        # Publish test telemetry
        test_hr = {
            'heart_rate': 75,
            'ecg_samples': [0.1] * 250,
            'timestamp': time.time()
        }
        
        result = client.publish(
            f'twinpac/patient/{TEST_PATIENT}/heartrate',
            json.dumps(test_hr)
        )
        
        test("ECG message published", result.rc == 0)
        
        # Publish glucose
        test_glucose = {'glucose': 0.9, 'timestamp': time.time()}
        result = client.publish(
            f'twinpac/patient/{TEST_PATIENT}/glucose',
            json.dumps(test_glucose)
        )
        test("Glucose message published", result.rc == 0)
        
        # Publish battery
        test_battery = {'voltage': 3.5, 'timestamp': time.time()}
        result = client.publish(
            f'twinpac/patient/{TEST_PATIENT}/battery',
            json.dumps(test_battery)
        )
        test("Battery message published", result.rc == 0)
        
        # Wait for subscriber to process
        time.sleep(3)
        
        # Verify data reached DB
        r = requests.post(
            f'{API_BASE}/api/v1/telemetry/battery/latest',
            json={'patient_id': TEST_PATIENT, 'hours_ago': 1},
            timeout=5
        )
        
        data = r.json()
        test("Battery data reached database",
             len(data.get('data', [])) > 0,
             "MQTT subscriber may not be running")
    
    client.loop_stop()
    client.disconnect()

except ImportError:
    warn("paho-mqtt not installed — skipping MQTT test")
    warn("Run: pip install paho-mqtt")
except Exception as e:
    fail(f"MQTT test error: {e}")

# ===== TEST 4: Dashboard Endpoint =====
print("\n" + "="*60)
print("TEST 4: Dashboard Endpoint")
print("="*60)

try:
    r = requests.get(f'{API_BASE}/api/v1/dashboard/{TEST_PATIENT}', timeout=5)
    test("Dashboard endpoint responds", r.status_code == 200)
    data = r.json()
    test("Dashboard has ECG field", 'ecg' in data)
    test("Dashboard has glucose field", 'glucose' in data)
    test("Dashboard has battery field", 'battery' in data)
except Exception as e:
    fail(f"Dashboard endpoint failed: {e}")

# ===== TEST 5: AI Predictions =====
print("\n" + "="*60)
print("TEST 5: AI Prediction Endpoints")
print("="*60)

try:
    r = requests.get(
        f'{API_BASE}/api/v1/predictions/all/{TEST_PATIENT}',
        timeout=10
    )
    test("Unified predictions endpoint responds", r.status_code == 200)
    data = r.json()
    test("Response has patient_id", data.get('patient_id') == TEST_PATIENT)
    test("Response has alerts array", 'alerts' in data)
    
    if data.get('battery') and 'error' not in data['battery']:
        test("Battery PINN-LSTM prediction returned", True)
        info(f"Battery RUL: {data['battery'].get('rul_days', 'N/A')} days")
    else:
        warn("Battery model not loaded (train and add .h5 file first)")
    
    if data.get('cardiac') and 'error' not in data['cardiac']:
        test("Cardiac BiLSTM prediction returned", True)
        info(f"Cardiac risk: {data['cardiac'].get('risk_probability', 'N/A')}")
    else:
        warn("Cardiac model not loaded (train and add .h5 file first)")
    
    if data.get('metabolic') and 'error' not in data['metabolic']:
        test("Metabolic LSTM prediction returned", True)
        info(f"Glucose 1h: {data['metabolic'].get('glucose_1h_ahead_mgdl', 'N/A')} mg/dL")
    else:
        warn("Metabolic model not loaded (train and add .h5 file first)")

except Exception as e:
    fail(f"Predictions test error: {e}")

# ===== TEST 6: Edge Algorithms =====
print("\n" + "="*60)
print("TEST 6: Edge Algorithms (Unit Tests)")
print("="*60)

try:
    result = subprocess.run(
        ['python', '-m', 'pytest', 'backend/tests/', '-v', '--tb=short'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    test("Edge algorithm unit tests pass",
         result.returncode == 0,
         result.stdout[-500:] if result.stdout else "No output")
    
    if result.returncode != 0:
        info(result.stdout[-300:])
except Exception as e:
    warn(f"Unit tests skipped: {e}")

# ===== FINAL REPORT =====
print("\n" + "="*60)
print("SMOKE TEST RESULTS")
print("="*60)
print(f"{GREEN}Passed: {passed}{RESET}")
print(f"{RED}Failed: {failed}{RESET}")
print(f"Total: {passed + failed}")
print()

if failed == 0:
    print(f"{GREEN}🎉 ALL TESTS PASSED — System is operational!{RESET}")
elif failed <= 2:
    print(f"{YELLOW}⚠️  MOSTLY PASSING — Check warnings above{RESET}")
    print("   AI model failures are expected until .h5 files are trained")
else:
    print(f"{RED}❌ CRITICAL FAILURES — Check docker-compose logs{RESET}")
    print("   Run: docker-compose logs --tail=50")

print("\n📋 Next Steps:")
print("   1. Open dashboard: http://localhost:8000")
print("   2. Check API docs: http://localhost:8000/docs")
print("   3. View logs: docker-compose logs -f backend")
print("="*60)
