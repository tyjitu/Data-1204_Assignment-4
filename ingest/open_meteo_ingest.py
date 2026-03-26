import requests, json
from datetime import datetime
import os

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": 43.65,
    "longitude": -79.38,
    "start_date": "2024-01-01",
    "end_date": "2025-03-20",
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum"
}

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()

ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
filename = f"data/bronze/open_meteo/weather_{ts}.json"

os.makedirs("data/bronze/open_meteo", exist_ok=True)

with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print(f"Saved {filename}")