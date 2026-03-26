import json
import pandas as pd
import glob
import os

""" # load raw bronze file
with open("data/bronze/open_meteo/weather_example.json", "r") as f:
    raw = json.load(f) """

    # get latest bronze file
files = glob.glob("data/bronze/open_meteo/*.json")
latest_file = max(files, key=os.path.getctime)

print(f"Reading {latest_file}")

# LOAD the file → this creates 'raw'
with open(latest_file, "r") as f:
    raw = json.load(f)
    
daily = raw["daily"]

# flatten into dataframe
df = pd.DataFrame({
    "date": daily["time"],
    "temp_max": daily["temperature_2m_max"],
    "temp_min": daily["temperature_2m_min"],
    "precipitation": daily["precipitation_sum"]
})

# --- transformations ---
df["date"] = pd.to_datetime(df["date"]).dt.date

df["temp_max"] = df["temp_max"].astype(float)
df["temp_min"] = df["temp_min"].astype(float)
df["precipitation"] = df["precipitation"].astype(float)

# handle missing values
df = df.fillna(0)

# select final columns
silver = df[["date", "temp_max", "temp_min", "precipitation"]]

# save
silver.to_csv("data/silver/open_meteo/daily_weather.csv", index=False)

print("Saved data/silver/open_meteo/daily_weather.csv")