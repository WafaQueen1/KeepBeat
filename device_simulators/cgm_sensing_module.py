import time
import json
import random
import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
TOPIC = "twinpacemaker/sensors/cgm"

def generate_cgm_data():
    # Simulate glucose variations focusing on Hyper/Hypo thresholds
    prob = random.random()
    if prob < 0.1:
        glucose = random.uniform(0.4, 0.69)  # Hypo
    elif prob > 0.9:
        glucose = random.uniform(2.51, 3.5)  # Hyper
    else:
        glucose = random.uniform(0.7, 2.5)   # Normal
    
    return {
        "sensor_id": "CGM_001",
        "glucose_level": round(glucose, 2),
        "timestamp": time.time(),
        "unit": "g/L"
    }

def main():
    client = mqtt.Client(client_id="cgm_simulator")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        print(f"CGM Simulator connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        
        while True:
            data = generate_cgm_data()
            client.publish(TOPIC, json.dumps(data))
            print(f"[CGM] Published: {data}")
            time.sleep(5)  # publish every 5 seconds for simulation
            
    except KeyboardInterrupt:
        print("\nStopping CGM Simulator...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
