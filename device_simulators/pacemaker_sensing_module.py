import time
import json
import random
import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
TOPIC = "twinpacemaker/sensors/pacemaker"

# Simplified Capacity Fade Physics State
battery_capacity = 100.0
cycles = 0

def generate_pacemaker_data():
    global battery_capacity, cycles
    
    heart_rate = random.randint(60, 100)
    
    # Physics-based capacity fade (simplified for data generation)
    # The actual RUL LSTM modeling will happen on the Cloud
    fade_rate = 0.001 * (1 + (cycles / 10000.0))
    battery_capacity = max(0.0, battery_capacity - fade_rate)
    cycles += 1
    
    # Pseudo RUL just for simulation (will be replaced by NASA-dataset based PyTorch model on Cloud)
    rul_cycles = max(0.0, (battery_capacity - 20.0) / fade_rate) if fade_rate > 0 else 0
    rul_days = rul_cycles / (24 * 60 * 60 / 5) # Assuming 5s ticks -> days
    
    return {
        "sensor_id": "PM_001",
        "heart_rate": heart_rate,
        "battery_level_percent": round(battery_capacity, 4),
        "capacity_fade_cycles": cycles,
        "estimated_rul_days_local": round(rul_days, 2),
        "timestamp": time.time()
    }

def main():
    client = mqtt.Client(client_id="pacemaker_simulator")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        print(f"Pacemaker Simulator connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        
        while True:
            data = generate_pacemaker_data()
            client.publish(TOPIC, json.dumps(data))
            print(f"[Pacemaker] Published: {data}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopping Pacemaker Simulator...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
