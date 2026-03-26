import pandas as pd
import os

# --- 1. Load Silver datasets ---
weather = pd.read_csv("data/silver/open_meteo/daily_weather.csv")
events = pd.read_csv("data/silver/nasa_eonet/daily_events.csv")

# --- 2. Merge datasets on 'date' ---
gold = weather.merge(events, on="date", how="outer")

# --- 3. Handle missing values ---
for col in ["temp_max", "temp_min", "precipitation", "event_count", "wildfire_count", "storm_count"]:
    if col in gold.columns:
        gold[col] = gold[col].fillna(0)

# Derived columns
gold["event_day"] = gold["event_count"].apply(lambda x: 1 if x > 0 else 0)
gold["rainy_day"] = (gold["precipitation"] > 5).astype(int)  # example threshold: 5 mm
gold["is_weekend"] = pd.to_datetime(gold["date"]).dt.dayofweek.isin([5,6]).astype(int)

# --- 4. Select analysis-ready columns ---
gold_final = gold[[
    "date",
    "temp_max",
    "temp_min",
    "precipitation",
    "rainy_day",
    "event_count",
    "wildfire_count",
    "storm_count",
    "event_day",
    "is_weekend"
]]

# --- 5. Save Gold dataset ---
os.makedirs("data/gold", exist_ok=True)
gold_final.to_csv("data/gold/nasa_weather_gold.csv", index=False)

print("Saved data/gold/nasa_weather_gold.csv")