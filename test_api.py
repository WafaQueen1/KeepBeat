#!/usr/bin/env python3
"""
دليل اختبار النظام الكامل - TwinPacemaker
Testing Guide - Exact Working Examples
"""

import requests
import json
import time
from datetime import datetime, timezone

# ============================================================
# 1. المتغيرات الأساسية / Basic Configuration
# ============================================================

API_BASE = "http://127.0.0.1:8000"
ADMIN_EMAIL = "julian.sterling@keepbeat.com"
ADMIN_PASSWORD = "password123"
DOCTOR_EMAIL = "emma.clark@keepbeat.com"
DOCTOR_PASSWORD = "password123"
PATIENT_ID = "srarah.jenkins@keepbeat.com"

def print_step(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(label, data, success=True):
    status = "✓ SUCCESS" if success else "✗ ERROR"
    print(f"{status}: {label}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()

# ============================================================
# 2. اختبار المصادقة / Authentication Testing
# ============================================================

def test_login():
    """اختبر تسجيل دخول الطبيب والمسؤول"""
    print_step("اختبار تسجيل الدخول / Login Testing")
    
    # LoginTest 1: Admin
    print("1️⃣  تسجيل دخول المسؤول (Admin)")
    response = requests.post(
        f"{API_BASE}/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        admin_data = response.json()
        print_result("Admin Login", admin_data)
        return admin_data["id"]
    else:
        print_result("Admin Login", response.json(), success=False)
        return None

def test_list_doctors(admin_id):
    """اعرض قائمة الأطباء / List Doctors"""
    print_step("اختبار عرض الأطباء / List Doctors")
    
    response = requests.get(f"{API_BASE}/api/v1/doctors")
    if response.status_code == 200:
        doctors = response.json()
        print_result("List Doctors", doctors)
        if doctors:
            return doctors[0]["id"]
    else:
        print_result("List Doctors", response.json(), success=False)
    return None

def test_list_patients(doctor_id):
    """اعرض قائمة مرضى الطبيب / List Patients for Doctor"""
    print_step("اختبار عرض المرضى / List Patients")
    
    # ✅ الطريقة الصحيحة: تمرير doctor_id كـ query parameter
    response = requests.get(
        f"{API_BASE}/api/v1/patients",
        params={"doctor_id": doctor_id}
    )
    if response.status_code == 200:
        patients = response.json()
        print_result("List Patients (Correct)", patients)
        return patients
    else:
        print_result("List Patients", response.json(), success=False)
        return []

def test_create_patient(doctor_id):
    """أنشئ مريض جديد / Create New Patient"""
    print_step("اختبار إنشاء مريض جديد / Create New Patient")
    
    new_patient = {
        "doctor_id": doctor_id,
        "full_name": "Test Patient From Script",
        "dob": "1990-05-15",
        "medical_id": "TP-TEST-001",
        "affiliation": "Test Hospital",
        "diagnosis_notes": "Test case for simulation"
    }
    
    response = requests.post(
        f"{API_BASE}/api/v1/patients",
        json=new_patient
    )
    if response.status_code == 200:
        patient = response.json()
        print_result("Create Patient", patient)
        return patient["id"]
    else:
        print_result("Create Patient", response.json(), success=False)
        return None

# ============================================================
# 3. اختبار البيانات الحيوية / Telemetry Testing
# ============================================================

def test_post_telemetry(patient_id):
    """أرسل بيانات حيوية / Post Telemetry Data"""
    print_step("اختبار إرسال البيانات الحيوية / Post Telemetry")
    
    # ECG
    print("📊 إرسال بيانات ضربات القلب (ECG)")
    ecg_payload = {
        "patient_id": patient_id,
        "telemetry_type": "ecg",
        "heart_rate": 82.5,
        "timestamp": datetime.now(timezone.utc).timestamp()
    }
    response = requests.post(
        f"{API_BASE}/api/v1/telemetry",
        json=ecg_payload
    )
    print_result("ECG Data", response.json())
    
    # Glucose
    print("📊 إرسال بيانات الجلوكوز (CGM)")
    glucose_payload = {
        "patient_id": patient_id,
        "telemetry_type": "glucose",
        "glucose_value": 138.5,
        "timestamp": datetime.now(timezone.utc).timestamp()
    }
    response = requests.post(
        f"{API_BASE}/api/v1/telemetry",
        json=glucose_payload
    )
    print_result("Glucose Data", response.json())
    
    # Battery
    print("📊 إرسال بيانات البطارية (Battery)")
    battery_payload = {
        "patient_id": patient_id,
        "telemetry_type": "battery",
        "battery_voltage": 3.78,
        "timestamp": datetime.now(timezone.utc).timestamp()
    }
    response = requests.post(
        f"{API_BASE}/api/v1/telemetry",
        json=battery_payload
    )
    print_result("Battery Data", response.json())

# ============================================================
# 4. اختبار التنبؤات / AI Predictions Testing
# ============================================================

def test_model_status():
    """تحقق من حالة النماذج / Check Model Status"""
    print_step("اختبار حالة نماذج الذكاء الاصطناعي / Model Status")
    
    response = requests.get(f"{API_BASE}/api/model/status")
    if response.status_code == 200:
        status = response.json()
        print_result("Model Status", status)
        return status
    else:
        print_result("Model Status", response.json(), success=False)
        return None

def test_cardiac_prediction():
    """اختبر تنبؤ القلب / Test Cardiac Prediction"""
    print_step("اختبار تنبؤ الأرجيتميا / Cardiac Prediction")
    
    import math
    samples = [math.sin(i/10.0) for i in range(187)]
    
    response = requests.post(
        f"{API_BASE}/api/model/cardiac/predict",
        json={"samples": samples}
    )
    if response.status_code == 200:
        result = response.json()
        print_result("Cardiac Prediction", result)
    else:
        print_result("Cardiac Prediction", response.json(), success=False)

def test_battery_prediction():
    """اختبر تنبؤ البطارية / Test Battery Prediction"""
    print_step("اختبار تنبؤ عمر البطارية / Battery RUL Prediction")
    
    seq = [[3.7 - i*0.01, 0.5, 1.8 - i*0.02, 37.0 + i*0.05] for i in range(30)]
    
    response = requests.post(
        f"{API_BASE}/api/model/battery/predict",
        json={"sequence": seq}
    )
    if response.status_code == 200:
        result = response.json()
        print_result("Battery Prediction", result)
    else:
        print_result("Battery Prediction", response.json(), success=False)

def test_metabolic_prediction():
    """اختبر تنبؤ الجلوكوز / Test Metabolic Prediction"""
    print_step("اختبار تنبؤ مستويات الجلوكوز / Metabolic Prediction")
    
    timeseries = [110 + i for i in range(12)]
    metadata = [0.5, 0.0, 1.0, 0.0, 0.1]
    
    response = requests.post(
        f"{API_BASE}/api/model/metabolic/predict",
        json={"timeseries": timeseries, "metadata": metadata}
    )
    if response.status_code == 200:
        result = response.json()
        print_result("Metabolic Prediction", result)
    else:
        print_result("Metabolic Prediction", response.json(), success=False)

def test_all_predictions(patient_id):
    """احصل على جميع التنبؤات معاً / Get All Predictions"""
    print_step("اختبار جميع التنبؤات / All Predictions")
    
    response = requests.get(
        f"{API_BASE}/api/v1/predictions/all/{patient_id}"
    )
    if response.status_code == 200:
        result = response.json()
        print_result("All Predictions", result)
    else:
        print_result("All Predictions", response.json(), success=False)

# ============================================================
# 5. تشغيل الاختبارات / Run All Tests
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  اختبار كامل النظام / Full System Test")
    print("="*60)
    print(f"الخادم / Server: {API_BASE}\n")
    
    # Test 1: Authentication
    admin_id = test_login()
    if not admin_id:
        print("❌ فشل تسجيل الدخول / Login failed - stopping")
        exit(1)
    
    # Test 2: List doctors
    doctor_id = test_list_doctors(admin_id)
    if not doctor_id:
        print("❌ فشل جلب الأطباء / Failed to list doctors")
        exit(1)
    
    # Test 3: List patients
    patients = test_list_patients(doctor_id)
    
    # Test 4: Create patient
    new_patient_id = test_create_patient(doctor_id)
    if new_patient_id:
        test_patient_id = new_patient_id
    else:
        test_patient_id = PATIENT_ID
    
    # Test 5: Post telemetry
    test_post_telemetry(test_patient_id)
    
    # Test 6: AI Models
    test_model_status()
    test_cardiac_prediction()
    test_battery_prediction()
    test_metabolic_prediction()
    test_all_predictions(test_patient_id)
    
    print("\n" + "="*60)
    print("  اكتمل الاختبار / Test Complete!")
    print("="*60 + "\n")
