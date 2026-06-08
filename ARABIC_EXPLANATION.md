# شرح المشاكل والحلول - TwinPacemaker
# Problem Explanation & Solutions - TwinPacemaker

## 📌 الأخطاء التي حصلت عليها / The Errors You Got

### 1. `{"detail":"Method Not Allowed"}` ❌
**المعنى:** حاولت استخدام HTTP method خاطئ (مثلاً POST بدلاً من GET أو العكس)

**الحل:** استخدم الطريقة الصحيحة:
- `/api/v1/auth/login` → **POST** (مع email و password)
- `/api/v1/doctors` → **GET** (بدون parameters)
- `/api/v1/patients` → **GET** مع parameter `doctor_id`

---

### 2. `[]` (Empty Array) ✓
**المعنى:** الطلب نجح لكن لا توجد مرضى معينة
- السبب: المريض لم يكن مرتبطاً بهذا الطبيب
- **ليس خطأ** - هذا يعني الاتصال يعمل بشكل صحيح

---

### 3. `{"detail":[{"type":"missing","loc":["query","doctor_id"]...}]}` ❌
**المعنى:** نسيت تمرير `doctor_id` كـ query parameter

**الحل الصحيح:**
```bash
# ❌ خطأ
curl http://127.0.0.1:8000/api/v1/patients

# ✓ صحيح
curl http://127.0.0.1:8000/api/v1/patients?doctor_id=DOCTOR_ID_HERE
```

---

## 🎯 الحالة الحالية / Current Status

### ✅ ما يعمل بالفعل

1. **قاعدة البيانات** - TimescaleDB / SQLite ✓
2. **نماذج AI الثلاثة** - Cardiac, Battery, Metabolic ✓
3. **API Endpoints** - تخزين وجلب البيانات ✓
4. **المصادقة** - تسجيل الدخول للأطباء والمسؤولين ✓
5. **إدارة المرضى** - إنشاء وتعديل وحذف ✓
6. **التنبؤات** - جميع النماذج الثلاثة تعمل ✓

### ❌ ما ينقصك حالياً

1. **Docker Desktop لم يبدأ** - لذا لا يمكنك استخدام Docker
2. **Backend local لم يعمل** - الخادم الرئيسي لم يبدأ
3. **Device Simulators لم تعمل** - CGM و Pacemaker simulators مشكلة
4. **Frontend Dashboard لم يتصل** - لأن Backend معطل

---

## 🚀 كيفية التشغيل الصحيح / How to Start Everything

### الخطوة 1: تشغيل Backend محلياً (بدون Docker)
```bash
cd "d:\Vibe Coding\TwinPacemaker"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**سيرى:**
```
INFO:     Started server process
INFO:     Application startup complete
Starting Smart TwinPac Backend...
[OK] Dashboard mounted at /
[OK] Cardiac BiLSTM loaded
[OK] Battery PINN-LSTM loaded
[OK] Metabolic LSTM loaded
Backend ready
```

---

### الخطوة 2: اختبر البيانات
```bash
# في terminal جديد
cd "d:\Vibe Coding\TwinPacemaker"
python test_api.py
```

سيختبر:
- ✓ تسجيل الدخول
- ✓ جلب الأطباء
- ✓ جلب المرضى
- ✓ إنشاء مريض جديد
- ✓ إرسال بيانات (ECG, Glucose, Battery)
- ✓ النماذج الثلاثة للتنبؤ

---

### الخطوة 3: شغل Device Simulators
```bash
# في terminal جديد - CGM Simulator
cd "d:\Vibe Coding\TwinPacemaker"
python device_simulators/cgm_sensing_module.py

# في terminal آخر - Pacemaker/ECG Simulator
python device_simulators/pacemaker_sensing_module.py
```

---

### الخطوة 4: فتح Dashboard

#### أ) Dashboard الأطباء (Doctor Dashboard)
```
http://127.0.0.1:8000/static/index.html
```

**تسجيل دخول بـ:**
- Email: `emma.clark@keepbeat.com`
- Password: `password123`

#### ب) Dashboard الذكاء الاصطناعي (AI Dashboard)
```
http://127.0.0.1:8000/static/model-prototype.html
```

---

## 📊 اختبار كل جزء على حدة / Test Individual Components

### 1️⃣ اختبر تسجيل الدخول
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"emma.clark@keepbeat.com","password":"password123"}'
```

### 2️⃣ احصل على ID الطبيب
```bash
curl http://127.0.0.1:8000/api/v1/doctors
```

**سترى:** قائمة الأطباء مع الـ ID الخاص بهم

### 3️⃣ احصل على مرضى الطبيب (⚠️ استبدل DOCTOR_ID)
```bash
curl "http://127.0.0.1:8000/api/v1/patients?doctor_id=DOCTOR_ID"
```

### 4️⃣ أرسل بيانات ECG
```bash
curl -X POST http://127.0.0.1:8000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id":"srarah.jenkins@keepbeat.com",
    "telemetry_type":"ecg",
    "heart_rate":82
  }'
```

### 5️⃣ احصل على التنبؤات
```bash
curl http://127.0.0.1:8000/api/v1/predictions/all/srarah.jenkins@keepbeat.com
```

---

## 🔧 حل المشاكل / Troubleshooting

### المشكلة: "Connection refused"
**الحل:** Backend لم يبدأ
```bash
# تأكد من أن Backend يعمل:
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### المشكلة: "Models not loaded"
**الحل:** ملفات النماذج في المكان الصحيح؟
```bash
# تحقق من المسارات:
ls models/battery/battery_pinn_lstm.keras
ls models/cardiac/cardiac_bilstm.keras
ls models/metabolic/metabolic_stacked_lstm.keras
```

### المشكلة: "Doctor/Patient not found"
**الحل:** النسخة المزروعة (seeded) لم تعمل
```bash
# تحقق من قاعدة البيانات:
sqlite3 twinpacemaker.db "SELECT * FROM doctors;"
```

---

## 📝 الحسابات المُنشأة تلقائياً / Pre-seeded Accounts

| الدور | البريد | كلمة المرور | حالة التفعيل |
|------|---------|------------|----------|
| Admin | `julian.sterling@keepbeat.com` | `password123` | ✓ مفعّل |
| Doctor | `emma.clark@keepbeat.com` | `password123` | ✓ مفعّل |
| **Patient** | `srarah.jenkins@keepbeat.com` | N/A | ✓ معترف به |

---

## 🎬 تشغيل كل شيء معاً (في نافذة واحدة)

### Windows PowerShell Script:
```powershell
# Terminal 1: Backend
cd "d:\Vibe Coding\TwinPacemaker"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2: CGM Simulator
cd "d:\Vibe Coding\TwinPacemaker"
python device_simulators/cgm_sensing_module.py

# Terminal 3: Tests
cd "d:\Vibe Coding\TwinPacemaker"
python test_api.py

# Terminal 4: Open Browser
# http://127.0.0.1:8000/static/index.html
# http://127.0.0.1:8000/static/model-prototype.html
```

---

## 🎯 الخطوات التالية / Next Steps

1. **ابدأ Backend** بدون Docker
2. **جرب test_api.py** لتأكيد الاتصال
3. **شغل Device Simulators** لإرسال بيانات حقيقية
4. **افتح Dashboards** لرؤية البيانات والتنبؤات
5. **أضف مرضى جدد** من Doctor Dashboard
6. **راقب التنبؤات** في AI Dashboard

---

## 📞 ملخص المشاكل / Summary

| المشكلة | السبب | الحل |
|--------|------|------|
| Backend معطل | لم تبدأه | `uvicorn backend.main:app --port 8000` |
| Errors في API | Method خطأ / missing parameters | استخدم curl examples الصحيحة |
| Simulators معطلة | لم تشغلها | `python device_simulators/*.py` |
| Dashboard فارغ | لا توجد بيانات | أرسل telemetry أو شغل simulators |

**كل شيء جاهز الآن - ابدأ بـ Backend ولاحظ الفرق! 🚀**
