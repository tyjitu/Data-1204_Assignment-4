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
- **Null hypothesis (H0):** The proportion of days with events is the same for rainy and non-rainy days.  
- **Alternative hypothesis (H1):** The proportion of days with events is different between rainy and non-rainy days.

## Suggested Statistical Test
- **Two-proportion z-test** — because both the outcome and grouping variables are binary, and we want to compare the proportion of event days between two groups (rainy vs. non-rainy).

## Notes on Analysis
- Other tests we could consider in Part 2 include:
  - One-sample t-test: e.g., comparing average temperature on event days vs. a reference value.
  - Two-sample t-test: e.g., comparing temperature on wildfire days vs. non-wildfire days.
  - Paired t-test: e.g., before-and-after comparisons if we incorporate temporal features.
  
- The current Gold dataset supports all of these because it includes:
  - Daily outcomes (`event_day`)
  - Weather variables (`temp_max`, `precipitation`)
  - Binary indicators (`rainy_day`, `is_weekend`, `wildfire_count > 0`)