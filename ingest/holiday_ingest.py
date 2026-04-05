import requests, json
from datetime import datetime
import os

year = "2024"
country_code = "US"
url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"

response = requests.get(url)
response.raise_for_status()
data = response.json()

ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
filename = f"data/bronze/holidays/us_holidays_{ts}.json"

os.makedirs("data/bronze/holidays", exist_ok=True)

with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print(f"Saved {filename}")
