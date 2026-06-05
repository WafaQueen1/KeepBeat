import asyncio
from bleak import BleakClient, BleakScanner
import requests
import json
import time

# UUIDs must match the ESP32 code
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

BACKEND_URL = "http://127.0.0.1:8000/api/v1/telemetry"
PATIENT_ID = "PT_001"

async def main():
    print("Scanning for TwinPacemaker_ESP32...")
    devices = await BleakScanner.discover()
    esp32_device = None
    for d in devices:
        if d.name and "TwinPacemaker" in d.name:
            esp32_device = d
            break

    if not esp32_device:
        print("❌ ESP32 not found. Ensure it is powered on and advertising.")
        return

    print(f"✅ Found {esp32_device.name} at {esp32_device.address}")

    async with BleakClient(esp32_device.address) as client:
        print("Connected to ESP32!")
        
        def notification_handler(sender, data):
            payload_str = data.decode('utf-8')
            if payload_str == "LEADS_OFF":
                print("⚠️ Leads off detected!")
                return
            
            try:
                ecg_val = float(payload_str)
                # In a real scenario, you'd buffer 187 samples before sending.
                # Here we simulate sending a heart rate approximation.
                # (For full ECG, buffer these values in an array).
                
                # Mock HR calculation for prototyping from single reading (not accurate, just for data pipeline)
                hr = 70.0 + (ecg_val % 10) 
                
                req_data = {
                    "patient_id": PATIENT_ID,
                    "telemetry_type": "ecg",
                    "heart_rate": hr,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                
                try:
                    res = requests.post(BACKEND_URL, json=req_data)
                    print(f"Sent: {req_data['heart_rate']} BPM -> Backend: {res.status_code}")
                except Exception as e:
                    pass
                
            except ValueError:
                pass

        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        print("Listening for ECG data... Press Ctrl+C to stop.")
        
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
