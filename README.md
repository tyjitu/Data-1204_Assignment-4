# NASA Events & Weather Data Pipeline

This project builds a **Bronze → Silver → Gold data pipeline** for NASA EONET events and Open-Meteo Historical Weather data.  
The pipeline ingests raw API data, transforms it into clean, analysis-ready datasets, and produces a Gold dataset suitable for statistical analysis and visualization.

---

## Project Overview

**Project Goal:**  
- Collect daily event data from NASA EONET (natural events like wildfires and storms)  
- Collect historical weather data (temperature, precipitation) from Open-Meteo  
- Clean, transform, and combine the datasets into a Gold table for analysis in Part 2  

**Learning Goals:**  
By the end of this assignment, you should be able to:

- Pull data programmatically from public APIs  
- Save raw snapshots and organize them into Bronze / Silver / Gold layers  
- Clean and standardize raw API data  
- Join multiple sources into one analysis-ready dataset  
- Design a dataset with future hypothesis testing in mind  
- Use AI tools productively while still understanding and documenting your work

**Pipeline Layers:**  
1. **Bronze:** Raw JSON files from APIs, timestamped.  
2. **Silver:** Flattened, cleaned, and structured CSVs with derived columns.  
3. **Gold:** Analysis-ready table combining weather and event data, with derived binary variables and indicators for easy statistical testing.

## Data Transformations

### Bronze → Silver

In this stage, raw API data is transformed into clean, structured datasets.

For NASA EONET:
- Parsed nested JSON into a flat structure  
- Extracted event dates from geometry fields  
- Converted timestamps into a standard `date` column  
- Aggregated events by date to create:
  - `event_count`
  - `wildfire_count`
  - `storm_count`  

For Open-Meteo:
- Extracted daily weather variables  
- Converted date strings into proper date format  
- Renamed columns for clarity (`temp_max`, `temp_min`, `precipitation`)  
- Ensured correct data types (numeric and date)  
- Handled missing values where necessary  

---

### Silver → Gold

In this stage, cleaned datasets are combined and enhanced for analysis.

- Joined NASA events and weather data on the `date` column  
- Used an outer join to retain all dates  
- Filled missing values (e.g., no events → 0)  
- Created derived features for statistical analysis:
  - `event_day` → whether any event occurred  
  - `rainy_day` → whether precipitation exceeded a threshold  
  - `is_weekend` → whether the date falls on a weekend  

---

### Purpose

These transformations ensure that the final dataset is:
- Clean and consistent  
- Aligned at the daily level  
- Ready for statistical testing and visualization in Part 2  

---

## Folder Structure
```text
project_root/
│
├─ data/
│   ├─ bronze/        # Raw API responses
│   │   ├─ nasa_eonet/
│   │   └─ open_meteo/
│   ├─ silver/        # Cleaned datasets
│   │   ├─ nasa_eonet/
│   │   └─ open_meteo/
│   └─ gold/          # Analysis-ready combined dataset
│
├─ ingest/            # API ingestion scripts
│   ├─ nasa_eonet_ingest.py
│   └─ open_meteo_ingest.py
│
├─ transform/         # Transformation scripts
│   ├─ nasa_eonet_transform.py
│   ├─ open_meteo_transform.py
│   └─ gold_nasa_weather.py
│
├─ notebooks/         # Jupyter notebooks for exploration
│   ├─ nasa_eonet.ipynb
│   └─ open_meteo.ipynb
│
├─ analysis_preview.md
└─ README.md
```

## AI Usage

In this project, I used ChatGPT (GPT-5) to assist with Python scripting, data pipeline structuring, and general guidance on building the Bronze → Silver → Gold workflow.

The AI helped with:

Writing ingestion scripts for NASA EONET and Open-Meteo APIs.
Transforming raw JSON into clean, analysis-ready Silver datasets.
Planning the Gold dataset structure and derived variables.


## Example of verification/fix:

While AI helped generate parts of the ingestion and transformation code, I took responsibility for verifying that all joins and transformations were correct. I carefully checked that datasets were properly aligned on the date key and ensured that missing values were handled appropriately after joining. I also reviewed the transformation logic to confirm that features like event_count, rainy_day, and event_day were created correctly and made sense for analysis. This process ensured that I fully understood the pipeline and that the final Gold dataset is reliable and suitable for future statistical testing.

## Next Steps (Part 2)

- Use the Gold dataset in a Streamlit app for interactive exploration

- Perform statistical tests:
-- One-sample t-tests
-- Two-sample t-tests
-- Paired t-tests
-- Proportion-based z-tests

- Answer questions like:
Does rainy weather have an effect on the occurrence of natural events, such as wildfires or storms?
How do temperature and precipitation relate to event frequency?

## Setup Instructions

1. **Clone the repository:**

git clone <repo-url>

cd <repo-name>

2. **Create a virtual environment:**

uv init

uv venv

.\.venv\Scripts\Activate.ps1      # Windows

3. **Install dependencies:**

uv add jupyterlab

uv add pandas numpy scipy statsmodels

4. **Run ingestion scripts (Bronze layer):**

python ingest/nasa_eonet_ingest.py

python ingest/open_meteo_ingest.py

5. **Run transformation scripts (Silver layer):**

python transform/nasa_eonet_transform.py

python transform/open_meteo_transform.py

6. **Build Gold dataset:**

python transform/gold_nasa_weather.py

