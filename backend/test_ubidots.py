import requests

TOKEN = "BBUS-7vlyFMJUpbcTFBzMIDpOIETRlIywN4"
DEVICE = "esp32"
VARIABLE = "sensor"

url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE}/{VARIABLE}/values/?page_size=5"
headers = {"X-Auth-Token": TOKEN}  # جربنا X-Auth-Token

print(f"🔍 Testing connection to: {url}")
print(f"🔑 Using Token: {TOKEN[:10]}...")

try:
    response = requests.get(url, headers=headers, timeout=5)
    print(f"\n📡 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! Data received:")
        print(data)
    else:
        print("❌ FAILED. Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection Error: {e}")