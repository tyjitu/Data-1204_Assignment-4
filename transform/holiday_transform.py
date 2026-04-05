import json
import glob
import os

import pandas as pd


files = glob.glob("data/bronze/holidays/*.json")
latest_file = max(files, key=os.path.getctime)

print(f"Reading {latest_file}")

with open(latest_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

holiday_df = pd.DataFrame(raw["holidays"])

holiday_df["date"] = pd.to_datetime(holiday_df["date"]).dt.date
holiday_df["holiday_flag"] = 1
holiday_df["holiday_name"] = holiday_df["name"].fillna(holiday_df.get("localName", "Holiday"))

silver = (
    holiday_df[["date", "holiday_flag", "holiday_name"]]
    .drop_duplicates(subset=["date"])
    .sort_values("date")
    .reset_index(drop=True)
)

os.makedirs("data/silver/holidays", exist_ok=True)
silver.to_csv("data/silver/holidays/daily_holidays.csv", index=False)

print("Saved data/silver/holidays/daily_holidays.csv")
