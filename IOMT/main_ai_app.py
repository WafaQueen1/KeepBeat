import os
import time
import requests
import numpy as np
import scipy.signal as signal
from tensorflow.keras.models import load_model

# 1. إعدادات سحب البيانات من السحابة (المُرسلة من جهاز PC 2: IoT)
TOKEN = "BBUS-2g7egqTyJKKteqn1lWCdrEVBKwAA4a" 
DEVICE_LABEL = "esp32"
VARIABLE_LABEL = "sensor"

# 2. إعدادات الـ Pipeline للفلاتر الرقمية
FS = 200  # التردد الفرضي لأخذ العينات (200 قراءة في الثانية)

# 3. المسار المطلق لنموذج الـ CNN-LSTM الخاص بكم على جهازكِ
MODEL_PATH = r"D:\Vibe Coding\TwinPacemaker\models\cardiac\cardiac2\best_model_cnn_lstm.keras"

if os.path.exists(MODEL_PATH):
    print("⏳ [1/2] جاري تحميل نموذج الذكاء الاصطناعي الـ CNN-LSTM...")
    keepbeat_model = load_model(MODEL_PATH)
    print("✅ تم تحميل نموذج (best_model_cnn_lstm.keras) بنجاح وهو جاهز للتشخيص!")
else:
    print(f"❌ خطأ: لم يتم العثور على ملف النموذج في المسار المحدد:")
    print(f"   {MODEL_PATH}")
    print("تأكدي من صحة الحروف أو أن الملف موجود فعلياً في هذا المجلد.")
    exit()

# 4. دالة الـ Pipeline لمعالجة وتصفية الإشارة الرقمية قبل إدخالها للنموذج
def apply_ecg_pipeline(raw_data):
    """
    تطبيق فلاتر التصفية والتطبيع بالتتابع (Cascade) لتنظيف الإشارة الخام
    """
    signal_array = np.array(raw_data)
    
    # ■ Filtre Passe-Bande (بين 0.5Hz و 45Hz) لإزالة تموجات التنفس والضوضاء العالية
    lowcut = 0.5
    highcut = 45.0
    nyquist = 0.5 * FS
    low = lowcut / nyquist
    high = highcut / nyquist
    b_band, a_band = signal.butter(3, [low, high], btype='band')
    bandpassed_signal = signal.filtfilt(b_band, a_band, signal_array)
    
    # ■ Filtre Coupe-Bande (Notch Filter عند 50Hz) لإزالة تشويش تيار الكهرباء المنزلي AC
    f0 = 50.0  # التردد المراد حذفه
    Q = 30.0   # عامل الجودة
    b_notch, a_notch = signal.iirnotch(f0, Q, FS)
    filtered_signal = signal.filtfilt(b_notch, a_notch, bandpassed_signal)
    
    # ■ Normalization (تطبيع الإشارة بين 0 و 1 لتتوافق مع مدخلات النموذج)
    min_val = np.min(filtered_signal)
    max_val = np.max(filtered_signal)
    if max_val != min_val:
        normalized_signal = (filtered_signal - min_val) / (max_val - min_val)
    else:
        normalized_signal = filtered_signal
        
    return normalized_signal

# 5. دالة جلب البيانات الحية من سحابة Ubidots
def get_live_ecg_window(window_size=187):
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/{VARIABLE_LABEL}/values/?page_size={window_size}"
    headers = {"X-OAuthToken": TOKEN}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            values = [item['value'] for item in response.json()['results']]
            values.reverse()  # ترتيب البيانات من الأقدم إلى الأكثر حداثة
            return values
    except Exception as e:
        print("❌ خطأ في الاتصال بالـ API وجلب البيانات:", e)
    return None

# 6. الحلقة التكرارية الرئيسية لتشغيل النظام في الوقت الفعلي (Real-time Execution)
print("\n🔥 [2/2] تم تشغيل النظام الموحد... في انتظار البيانات الحية من (PC 2: IoT)...")
print("─" * 70)

# مخرجات تصنيف فئات نبضات القلب لـ MIT-BIH (Normal, Supraventricular, Ventricular, Fusion, Unknown)
CLASSES = ['Normal (طبيعي)', 'Supraventricular (فوق بطيني)', 'Ventricular (بطيني / خطير)', 'Fusion (مدمج)', 'Unknown (غير معروف)']

try:
    while True:
        # سحب النافذة الزمنية (187 عينة المطلوبة للموديل)
        raw_signal = get_live_ecg_window(window_size=187)
        
        if raw_signal and len(raw_signal) == 187:
            # أ) تمرير الإشارة الخام داخل الـ Pipeline لتنظيفها وتصفيتها
            clean_signal = apply_ecg_pipeline(raw_signal)
            
            # ب) إعادة تشكيل أبعاد مصفوفة الـ Numpy لتتوافق مع مدخلات الـ CNN-LSTM (1, 187, 1)
            input_data = clean_signal.reshape(1, 187, 1)
            
            # ج) إرسال مصفوفة الـ Pipeline النظيفة مباشرة إلى نموذج الكيراس للتوقع
            predictions = keepbeat_model.predict(input_data, verbose=0)
            class_index = np.argmax(predictions[0])
            confidence = predictions[0][class_index] * 100
            
            # د) عرض النتائج ومستوى الخطورة الطبي فوراً على الشاشة
            print(f"📊 [إشارة جديدة]: تم استقبال وتنظيف 187 قراءة بنجاح.")
            print(f"🔮 [التشخيص الطبي]: {CLASSES[class_index]}")
            print(f"🎯 [نسبة اليقين والثقة]: {confidence:.2f}%")
            
            # تحديد مستوى التنبيه التلقائي للمنظومة الذكية
            if class_index == 0:
                print("🟢 مستوى الخطورة: منخفض (RISK LEVEL: LOW) - حالة مستقرة")
            else:
                print("🔴 تنبيه طبي: تم رصد اضطراب في النبض (RISK LEVEL: HIGH)!")
            print("─" * 70 + "\n")
            
        else:
            print("⏳ في انتظار تدفق قراءات كافية من لوحة الـ ESP32 على السحابة...")
            
        time.sleep(1.5)  # تحديث البيانات وإعطاء تشخيص جديد كل ثانية ونصف
except KeyboardInterrupt:
    print("\n🛑 تم إيقاف تشغيل سكريبت الذكاء الاصطناعي بنجاح.")