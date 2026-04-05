# Assignment 4 Analysis Plan

## 1. New source added

For Assignment 4, I added a third data source: U.S. public holiday data from the Nager.Date Public Holidays API.

- Source: `https://date.nager.at`
- Endpoint pattern: `/api/v3/PublicHolidays/{year}/US`
- Why it belongs in the project:
  The original project already analyzed daily weather and daily NASA EONET events. Holiday context adds a simple but meaningful behavioral and calendar-based grouping feature that can support clearer comparisons in the Streamlit app.

## 2. Join key

The holiday data is joined to the Assignment 3 Gold foundation using the daily `date` column.

- NASA EONET silver data is aggregated to daily event counts by `date`
- Open-Meteo silver data is already daily by `date`
- Holiday data is transformed to one row per holiday `date`

This keeps all three sources aligned at the same daily grain.

## 3. New variables created

The new source enabled these Assignment 4 variables:

- `holiday_flag`
  `1` if the date is a U.S. public holiday, otherwise `0`
- `holiday_name`
  holiday name from the joined holiday dataset, or `Not a holiday`
- `holiday_or_weekend`
  derived grouping variable equal to `1` when a day is either a holiday or a weekend

These variables strengthen the dataset by adding an interpretable calendar grouping dimension beyond weather alone.

## 4. Dashboard story / question

The dashboard asks:

How do daily weather conditions and calendar context relate to whether a day contains at least one recorded natural event?

The app tells this story in a sequence:

1. show the combined dataset and derived features
2. show visuals that compare event and non-event days
3. test whether precipitation patterns differ across groups
4. test whether rainy-day status is associated with event-day frequency
5. reflect on why these are associative relationships, not causal proof

## 5. Required analyses

### One-sample t-test

- Question:
  Is the mean daily precipitation in the filtered sample different from `0` mm?
- Variables:
  `precipitation`
- Null hypothesis:
  Mean precipitation equals `0`
- Alternative hypothesis:
  Mean precipitation is different from `0`

### Two-sample t-test

- Question:
  Does mean precipitation differ between `event_day = 1` and `event_day = 0`?
- Variables:
  `precipitation` by `event_day`
- Null hypothesis:
  Mean precipitation is the same in both groups
- Alternative hypothesis:
  Mean precipitation differs between groups

### Chi-square test of independence

- Question:
  Is `event_day` independent of `rainy_day`?
- Variables:
  `event_day`, `rainy_day`
- Null hypothesis:
  The two categorical variables are independent
- Alternative hypothesis:
  They are associated

### Variance comparison

- Question:
  Is precipitation variability different on holiday versus non-holiday days?
- Variables:
  `precipitation` by `holiday_flag`
- Method:
  Levene's test
- Null hypothesis:
  The group variances are equal
- Alternative hypothesis:
  The group variances differ

### Correlation analysis

- Question:
  Is precipitation associated with `event_count`?
- Variables:
  `precipitation`, `event_count`
- Method:
  Spearman correlation
- Null hypothesis:
  No monotonic association exists
- Alternative hypothesis:
  A monotonic association exists

## 6. Supporting visualizations

- Time-series line chart:
  daily precipitation and event counts over time
- Boxplot:
  precipitation on event days versus non-event days
- Grouped bar chart:
  rainy versus non-rainy counts split by event-day status
- Scatterplot:
  precipitation versus event count

Each chart is included to motivate a later test rather than just display data.

## 7. Method justification

### One-sample t-test justification

This is appropriate because precipitation is continuous and the test compares the sample mean to a reference value. It is mainly useful as a baseline check showing the filtered sample is not centered at zero rainfall.

### Two-sample t-test justification

This is appropriate because precipitation is continuous and `event_day` creates two independent groups. Welch's version is used because the group sizes and variances may differ.

### Chi-square justification

This is appropriate because both `event_day` and `rainy_day` are categorical variables. The test checks whether the occurrence of event days is associated with rainy versus non-rainy conditions. The main assumption to check is whether expected counts are large enough for the chi-square approximation to be reasonable.

### Variance comparison justification

Levene's test is used instead of a classic F-test because precipitation data can be skewed and zero-heavy. That makes Levene's test a safer variance-comparison method for this project.

### Correlation justification

Spearman correlation fits better than Pearson here because `event_count` is a count variable and the relationship may be monotonic without being linear.

## 8. Limits and cautions I will explain in the app

- Daily joins ignore within-day timing
- EONET counts depend on recorded events and category definitions
- Holiday context may affect reporting patterns or human activity, but it does not prove causation
- Statistical significance does not automatically imply practical importance
- Calendar effects, seasonality, and sample size may influence the results
