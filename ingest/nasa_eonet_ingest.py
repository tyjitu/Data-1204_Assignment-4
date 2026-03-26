import requests, json
from datetime import datetime
import os

url = "https://eonet.gsfc.nasa.gov/api/v3/events"

params = { "status": "all",
    "start": "2024-01-01",
    "end": "2024-12-31",
    "category": "wildfires,severeStorms"}  # no params needed, but kept for consistency

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()

ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
filename = f"data/bronze/nasa_eonet/events_{ts}.json"

os.makedirs("data/bronze/nasa_eonet", exist_ok=True)

with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print(f"Saved {filename}")