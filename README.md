# Assignment 4: NASA Events, Weather, and Holiday Data Pipeline

This project builds a **Bronze -> Silver -> Gold data pipeline** for NASA EONET events, Open-Meteo historical weather data, and U.S. public holiday data.
The pipeline ingests raw API data, transforms it into clean, analysis-ready datasets, and produces a Gold dataset suitable for statistical analysis, visualization, and the Streamlit app.

---

## Project Overview

**Project Goal:**
- Collect daily event data from NASA EONET (natural events like wildfires and storms)
- Collect historical weather data (temperature, precipitation) from Open-Meteo
- Collect U.S. public holiday data from Nager.Date
- Clean, transform, and combine the datasets into a Gold table for analysis in Part 2

**Learning Goals:**
By the end of this assignment, you should be able to:

- Pull data programmatically from public APIs
- Save raw snapshots and organize them into Bronze / Silver / Gold layers
- Clean and standardize raw API data
- Join multiple sources into one analysis-ready dataset
- Design a dataset with future hypothesis testing in mind
- Build a Streamlit app that connects the data story to statistical testing
- Use AI tools productively while still understanding and documenting my own work

**Pipeline Layers:**
1. **Bronze:** Raw JSON files from APIs, timestamped.
2. **Silver:** Flattened, cleaned, and structured CSVs with derived columns.
3. **Gold:** Analysis-ready table combining weather, event, and holiday data, with derived binary variables and indicators for easy statistical testing.

## Data Transformations

### Bronze -> Silver

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

For Nager.Date:
- Extracted U.S. public holiday records
- Standardized holiday dates into the shared `date` column
- Prepared holiday fields for joining and analysis

---

### Silver -> Gold

In this stage, cleaned datasets are combined and enhanced for analysis.

- Joined NASA events, weather data, and holiday data on the `date` column
- Used an outer join to retain all dates
- Filled missing values (for example, no events -> 0)
- Created derived features for statistical analysis:
  - `event_day` -> whether any event occurred
  - `rainy_day` -> whether precipitation exceeded a threshold
  - `is_weekend` -> whether the date falls on a weekend
  - `holiday_flag` -> whether the date is a U.S. public holiday
  - `holiday_name` -> the name of the holiday on matching dates
  - `holiday_or_weekend` -> whether the date is either a holiday or a weekend

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
|
|-- data/
|   |-- bronze/        # Raw API responses
|   |   |-- nasa_eonet/
|   |   |-- open_meteo/
|   |   `-- holidays/
|   |-- silver/        # Cleaned datasets
|   |   |-- nasa_eonet/
|   |   |-- open_meteo/
|   |   `-- holidays/
|   `-- gold/          # Analysis-ready combined dataset
|
|-- ingest/            # API ingestion scripts
|   |-- nasa_eonet_ingest.py
|   |-- open_meteo_ingest.py
|   `-- holiday_ingest.py
|
|-- transform/         # Transformation scripts
|   |-- nasa_eonet_transform.py
|   |-- open_meteo_transform.py
|   |-- holiday_transform.py
|   `-- gold_nasa_weather.py
|
|-- notebooks/         # Jupyter notebooks for exploration
|   |-- holidays.ipynb
|   |-- nasa_eonet.ipynb
|   `-- open_meteo.ipynb
|
|-- app/
|   `-- streamlit_app.py
|
|-- assignment4_analysis_plan.md
|-- assignment4_reflection.md
|-- requirements.txt
`-- README.md
```

## AI Usage

In this project, I used ChatGPT (GPT-5) to assist with Python scripting, data pipeline structuring, Streamlit app planning, and general guidance on building the Bronze -> Silver -> Gold workflow.

The AI helped with:

Writing ingestion scripts for NASA EONET and Open-Meteo APIs.
Adding and transforming the holiday data source for Assignment 4.
Transforming raw JSON into clean, analysis-ready Silver datasets.
Planning the Gold dataset structure, derived variables, and analysis flow.

## Example of verification/fix:

While AI helped generate parts of the ingestion and transformation code, I took responsibility for verifying that all joins and transformations were correct. I carefully checked that datasets were properly aligned on the date key and ensured that missing values were handled appropriately after joining. I also reviewed the transformation logic to confirm that features like `event_count`, `rainy_day`, `event_day`, and `holiday_flag` were created correctly and made sense for analysis. This process ensured that I fully understood the pipeline and that the final Gold dataset is reliable and suitable for statistical testing in Assignment 4.

## Assignment 4 Analysis Focus

- Use the Gold dataset in a Streamlit app for interactive exploration

- Perform statistical tests:
-- One-sample t-tests
-- Two-sample t-tests
-- Chi-square tests of independence
-- Variance comparisons
-- Correlation analysis

- Answer questions like:
Is the occurrence of a natural event associated with whether a day is rainy?
How do temperature and precipitation relate to event frequency?
Is holiday status associated with whether a day contains at least one recorded natural event?

## Setup Instructions

1. **Clone the repository:**

```bash
git clone <repo-url>
cd <repo-name>
```

2. **Create a virtual environment:**

```bash
uv init
uv venv
.\.venv\Scripts\Activate.ps1
```

3. **Install dependencies:**

```bash
uv add jupyterlab
uv add pandas numpy scipy statsmodels streamlit altair
```

4. **Run ingestion scripts (Bronze layer):**

```bash
python ingest/nasa_eonet_ingest.py
python ingest/open_meteo_ingest.py
python ingest/holiday_ingest.py
```

5. **Run transformation scripts (Silver layer):**

```bash
python transform/nasa_eonet_transform.py
python transform/open_meteo_transform.py
python transform/holiday_transform.py
```

6. **Build Gold dataset:**

```bash
python transform/gold_nasa_weather.py
```

7. **Run the Streamlit app:**

```bash
streamlit run app/streamlit_app.py
```
