import os
import time
import json
import requests
import serial
import threading
import argparse

# Configuration
API_ENDPOINT = "http://localhost:8000/api/model/cardiac/predict"

def parse_line(line):
    # Expecting either JSON like: { "device_id": "esp32", "samples": [187...] }
    # Or a comma-separated list of 187 integers.
    try:
        data = json.loads(line)
        if "samples" in data:
            return data["samples"]
    except json.JSONDecodeError:
        pass
        
    try:
        parts = [float(x.strip()) for x in line.split(",")]
        if len(parts) == 187:
            return parts
    except ValueError:
        pass
        
    return None

def main():
    parser = argparse.ArgumentParser(description="TwinPacemaker Bluetooth Relay")
    parser.add_argument("--port", type=str, default="COM3", help="Bluetooth Serial COM port (e.g., COM3 on Windows or /dev/ttyUSB0 on Linux)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    parser.add_argument("--api", type=str, default=API_ENDPOINT, help="Backend predict API endpoint")
    args = parser.parse_args()

    print(f"Starting Bluetooth Relay on {args.port} at {args.baud} baud")
    print(f"Forwarding to {args.api}")
    
    try:
        ser = serial.Serial(args.port, args.baud, timeout=2.0)
    except Exception as e:
        print(f"Error opening serial port {args.port}: {e}")
        print("Please check your Bluetooth settings and pair your device.")
        return

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
                
            samples = parse_line(line)
            if samples and len(samples) == 187:
                print(f"Received valid 187-sample window. Forwarding...")
                try:
                    resp = requests.post(args.api, json={"samples": samples}, timeout=2.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        print(f"Prediction: {data.get('label')} ({data.get('confidence_percent', 0):.1f}%)")
                    else:
                        print(f"API Error: {resp.status_code} - {resp.text}")
                except Exception as e:
                    print(f"Failed to reach API: {e}")
            else:
                print(f"Ignored line: {line[:50]}...")
                
        except serial.SerialException as e:
            print(f"Serial read error: {e}")
            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
            break

if __name__ == "__main__":
    main()
