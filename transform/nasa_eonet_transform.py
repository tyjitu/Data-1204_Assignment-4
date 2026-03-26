import json
import pandas as pd
import glob
import os

""" # load raw bronze file (replace with your actual filename if needed)
with open("data/bronze/nasa_eonet/events_example.json", "r") as f:
    raw = json.load(f) """

# get latest bronze file
files = glob.glob("data/bronze/nasa_eonet/*.json")
latest_file = max(files, key=os.path.getctime)

print(f"Reading {latest_file}")

with open(latest_file, "r") as f:
    raw = json.load(f)

rows = []

# flatten JSON
for event in raw["events"]:
    category = event["categories"][0]["title"] if event.get("categories") else None

    for geo in event.get("geometry", []):
        rows.append([
            geo.get("date"),
            category
        ])

# create dataframe
df = pd.DataFrame(rows, columns=["date", "category"])

# --- transformations ---
df["date"] = pd.to_datetime(df["date"]).dt.date
df["category"] = df["category"].fillna("unknown")

# --- aggregate to daily ---
daily = df.groupby("date").agg(
    event_count=("category", "count"),
    wildfire_count=("category", lambda x: (x == "Wildfires").sum()),
    storm_count=("category", lambda x: (x == "Severe Storms").sum())
).reset_index()

# save silver
daily.to_csv("data/silver/nasa_eonet/daily_events.csv", index=False)

print("Saved data/silver/nasa_eonet/daily_events.csv")