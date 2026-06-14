import time
from backend.services.cardiac_prediction_service import get_cardiac_service

print("🚀 Starting Smart Cardiac Monitor...")
print("💡 Mode: Auto-Switching (Live -> DB -> Synthetic)")

service = get_cardiac_service()

try:
    while True:
        print("\n--- New Prediction Cycle ---")
        
        # This will try Ubidots -> DB -> Synthetic automatically
        result = service.predict_smart(db=None, patient_id=None)
        
        print(f"📊 Source: {result.get('data_source')}")
        print(f"⚖️ Risk Level: {result.get('risk_level')}")
        print(f"📈 Probability: {result.get('risk_probability'):.2f}")
        
        # Wait for 2 seconds before next check
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n🛑 Monitor stopped by user.")