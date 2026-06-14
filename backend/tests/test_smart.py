import sys
import os
# إضافة المسار الرئيسي للمشروع ليتمكن البرنامج من رؤية مجلد backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.services.cardiac_prediction_service import get_cardiac_service

service = get_cardiac_service()
# لن نمرر db أو patient_id حالياً، سيستخدم الـ Fallback تلقائياً
result = service.predict_smart(db=None, patient_id=None) 
print("Prediction Result:", result)