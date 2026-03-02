import requests
import time
import random

def run_simulator():
    print("Starting sensor simulation... Press Ctrl+C to stop.")
    while True:
        data = {
            "building_id": random.randint(1, 3),
            "sensor_id": "MAIN-PWR",
            "value": round(random.uniform(10.0, 60.0), 2)
        }
        try:
            requests.post("http://localhost:8001/ingest", json=data)
            print(f"Sent: Building {data['building_id']} - {data['value']} kWh")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    run_simulator()