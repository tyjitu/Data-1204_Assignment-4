# Assignment 4 Reflection

## What worked well

The Bronze to Silver to Gold pipeline from Assignment 3 made Assignment 4 much easier to extend. Because the original project already used a clean daily `date` key, I could add a holiday source without redesigning the full dataset. The Streamlit app also benefited from having a compact Gold dataset with both continuous and categorical variables already prepared.

## What was difficult

The hardest part was making sure the statistical tests felt motivated by the story instead of feeling forced. It was easy to choose tests mechanically, but harder to make each chart and each test support a coherent question about weather, calendar context, and natural-event days. Another challenge was deciding how to add a new source that was simple enough to explain while still improving the analysis.

## What assumptions were hardest to defend

The hardest assumptions to defend were independence and causation-related assumptions.

- Daily observations are treated as separate rows, but real-world event patterns can have temporal dependence.
- Holiday status is only a contextual grouping variable. A significant result would still show association, not proof that holidays cause events.
- The chi-square test depends on expected cell counts being reasonable.
- T-tests and variance comparisons are sensitive to skewness, unequal spread, and zero-heavy precipitation values.

## What I would improve for a larger analytics product

If this project became a larger analytics product, I would improve it in four ways.

1. I would add more geographic detail so the event data and weather data could be compared by region instead of only by date.
2. I would add more external context, such as wildfire smoke, climate normals, or mobility data, to build a stronger explanatory story.
3. I would add more rigorous assumption checks and effect-size reporting so the app emphasized practical importance along with p-values.
4. I would make the dashboard more interactive by letting users choose variables, compare event categories separately, and download filtered analysis outputs.
