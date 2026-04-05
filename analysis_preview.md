# Statistical Analysis Preview — Part 2

## Planned Statistical Question
Does rainy weather have an effect on the occurrence of natural events, such as wildfires or storms?

## Outcome Variable
- `event_day` — a binary variable indicating whether any NASA event occurred on that day.

## Grouping Variable
- `rainy_day` — a binary variable indicating whether precipitation exceeded 5 mm.

## Binary Variable Example
- `event_day` (1 = event occurred, 0 = no event)  
We created this variable to allow proportion-based tests and to quantify the presence or absence of events on any given day.

## Null and Alternative Hypotheses
- **Null hypothesis (H0):** `event_day` and `rainy_day` are independent. The occurrence of at least one natural event does not differ between rainy and non-rainy days.  
- **Alternative hypothesis (H1):** `event_day` and `rainy_day` are associated. The occurrence of at least one natural event differs between rainy and non-rainy days.

## Suggested Statistical Test
- **Chi-square test of independence** — because both `event_day` and `rainy_day` are binary categorical variables, and the goal is to test whether event occurrence is associated with rainy versus non-rainy conditions.

## Notes on Analysis
- Other tests we could consider in Part 2 include:
  - One-sample t-test: e.g., comparing average temperature on event days vs. a reference value.
  - Two-sample t-test: e.g., comparing temperature on wildfire days vs. non-wildfire days.
  - Paired t-test: e.g., before-and-after comparisons if we incorporate temporal features.
  
- The current Gold dataset supports all of these because it includes:
  - Daily outcomes (`event_day`)
  - Weather variables (`temp_max`, `precipitation`)
  - Binary indicators (`rainy_day`, `is_weekend`, `wildfire_count > 0`)

## Gold dataset has:

1. Continuous Metric

- These are numeric variables we can average or run t-tests on:

  - temp_max
  - temp_min
  - precipitation
  - event_count
  - wildfire_count
  - storm_count

**Example:**

- “I can use precipitation as a continuous variable to compare average rainfall between event and non-event days.”

2. Binary Variable

- These are Binary Variables :

  - event_day → 0 or 1
  - rainy_day → 0 or 1
  - is_weekend → 0 or 1

**Example:**

- “event_day is a binary variable indicating whether any natural event occurred.”

3. Grouping Variable

- These define groups for comparison:

  - rainy_day → rainy vs non-rainy
  - is_weekend → weekend vs weekday


**Example:**

- “I can use rainy_day as a grouping variable to compare event occurrence between rainy and non-rainy days.”
