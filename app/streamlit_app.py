from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from scipy import stats


st.set_page_config(
    page_title="Assignment 4 Statistical Analysis App",
    page_icon="",
    layout="wide",
)


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "gold" / "nasa_weather_gold.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["holiday_label"] = df["holiday_flag"].map({0: "Non-holiday", 1: "Holiday"})
    df["event_label"] = df["event_day"].map({0: "No event day", 1: "Event day"})
    df["rain_label"] = df["rainy_day"].map({0: "Non-rainy day", 1: "Rainy day"})
    df["weekend_label"] = df["is_weekend"].map({0: "Weekday", 1: "Weekend"})
    df["holiday_window_label"] = df["holiday_or_weekend"].map(
        {0: "Regular weekday", 1: "Holiday or weekend"}
    )
    df["month"] = df["date"].dt.strftime("%b %Y")

    return df.sort_values("date").reset_index(drop=True)


def fmt_p_value(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    if value < 0.001:
        return "< 0.001"
    return f"{value:.4f}"


def describe_significance(p_value: float) -> str:
    if pd.isna(p_value):
        return "The app could not compute a valid p-value for this filtered sample."
    if p_value < 0.05:
        return "The result is statistically significant at the 0.05 level."
    return "The result is not statistically significant at the 0.05 level."


def safe_spearman(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    subset = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(subset) < 3 or subset["x"].nunique() < 2 or subset["y"].nunique() < 2:
        return float("nan"), float("nan")
    return stats.spearmanr(subset["x"], subset["y"])


def safe_ttest_1samp(values: pd.Series, popmean: float) -> tuple[float, float]:
    sample = values.dropna()
    if len(sample) < 2:
        return float("nan"), float("nan")
    return stats.ttest_1samp(sample, popmean=popmean)


def safe_ttest_ind(group_a: pd.Series, group_b: pd.Series) -> tuple[float, float]:
    a = group_a.dropna()
    b = group_b.dropna()
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    return stats.ttest_ind(a, b, equal_var=False)


def safe_chi_square(table: pd.DataFrame) -> tuple[float, float, int, pd.DataFrame]:
    if table.empty or table.shape[0] < 2 or table.shape[1] < 2:
        return float("nan"), float("nan"), 0, pd.DataFrame()
    chi2, p_value, dof, expected = stats.chi2_contingency(table)
    expected_df = pd.DataFrame(expected, index=table.index, columns=table.columns)
    return chi2, p_value, dof, expected_df


def safe_levene(group_a: pd.Series, group_b: pd.Series) -> tuple[float, float]:
    a = group_a.dropna()
    b = group_b.dropna()
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    return stats.levene(a, b, center="median")


def render_test_result(
    title: str,
    hypotheses: list[str],
    stat_label: str,
    stat_value: float,
    p_value: float,
    explanation: str,
    interpretation: str,
    extra_lines: list[str] | None = None,
) -> None:
    st.subheader(title)
    for line in hypotheses:
        st.write(line)
    if extra_lines:
        for line in extra_lines:
            st.write(line)
    st.write(f"{stat_label}: {stat_value:.3f}" if pd.notna(stat_value) else f"{stat_label}: N/A")
    st.write(f"p-value: {fmt_p_value(p_value)}")
    st.info(explanation)
    st.success(describe_significance(p_value))
    st.write(interpretation)


df = load_data()

st.title("Assignment 4: Weather, Natural Events, and Holiday Context")
st.markdown(
    """
This Streamlit app continues the Assignment 3 NASA EONET + Open-Meteo project by adding a
third source: U.S. public holiday data from Nager.Date. The goal is to move from a merged
Gold dataset to a guided statistical story about when natural-event days appear and how
weather patterns change across those days.
"""
)

with st.sidebar:
    st.header("Filters")
    start_date, end_date = st.date_input(
        "Date range",
        value=(df["date"].min().date(), df["date"].max().date()),
        min_value=df["date"].min().date(),
        max_value=df["date"].max().date(),
    )

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    include_only = st.selectbox(
        "Subset view",
        [
            "All days",
            "Only rainy days",
            "Only non-rainy days",
            "Only event days",
            "Only non-event days",
        ],
    )

    filtered = df[
        (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
    ].copy()

    if include_only == "Only rainy days":
        filtered = filtered[filtered["rainy_day"] == 1]
    elif include_only == "Only non-rainy days":
        filtered = filtered[filtered["rainy_day"] == 0]
    elif include_only == "Only event days":
        filtered = filtered[filtered["event_day"] == 1]
    elif include_only == "Only non-event days":
        filtered = filtered[filtered["event_day"] == 0]

if filtered.empty:
    st.error("No rows remain after filtering. Expand the date range or choose a different subset.")
    st.stop()

st.header("1. Project Overview and Data Story")
st.write(
    """
The Assignment 3 Gold dataset joins daily NASA EONET event counts with Open-Meteo daily
weather using `date` as the key. For Assignment 4, the pipeline adds Nager.Date public
holiday data on that same daily grain, which creates `holiday_flag`, `holiday_name`, and
`holiday_or_weekend`. That lets the app keep calendar context in view while asking whether
event-day patterns differ on rainy versus non-rainy days, and whether weather conditions on
event days look different from non-event days.
"""
)

overview_col_1, overview_col_2, overview_col_3, overview_col_4 = st.columns(4)
overview_col_1.metric("Rows in view", f"{len(filtered):,}")
overview_col_2.metric("Event days", f"{int(filtered['event_day'].sum()):,}")
overview_col_3.metric("Holiday days", f"{int(filtered['holiday_flag'].sum()):,}")
overview_col_4.metric("Mean precipitation", f"{filtered['precipitation'].mean():.2f} mm")

st.header("2. Data Preview")

column_info = pd.DataFrame(
    [
        {"column": "date", "type": "date", "description": "Daily join key used across all sources."},
        {
            "column": "temp_max / temp_min",
            "type": "continuous",
            "description": "Daily maximum and minimum temperature from Open-Meteo.",
        },
        {
            "column": "precipitation",
            "type": "continuous",
            "description": "Daily precipitation in millimetres; used in t-tests and correlation.",
        },
        {
            "column": "event_count",
            "type": "count",
            "description": "Number of NASA EONET events recorded on that date.",
        },
        {
            "column": "event_day",
            "type": "binary",
            "description": "Derived flag equal to 1 when `event_count` is greater than 0.",
        },
        {
            "column": "rainy_day",
            "type": "binary",
            "description": "Derived flag equal to 1 when precipitation is greater than 5 mm.",
        },
        {
            "column": "is_weekend",
            "type": "binary",
            "description": "Derived weekend indicator from the calendar date.",
        },
        {
            "column": "holiday_flag",
            "type": "binary",
            "description": "Assignment 4 extension flag from the Nager.Date holiday source.",
        },
        {
            "column": "holiday_name",
            "type": "categorical",
            "description": "Holiday name from the joined holiday dataset, or `Not a holiday`.",
        },
        {
            "column": "holiday_or_weekend",
            "type": "binary",
            "description": "Derived grouping flag for days that are holidays or weekends.",
        },
    ]
)

preview_col, stats_col = st.columns([1.4, 1])
with preview_col:
    st.subheader("Sample rows")
    st.dataframe(filtered.head(10), use_container_width=True)
with stats_col:
    st.subheader("Summary statistics")
    st.dataframe(
        filtered[
            [
                "temp_max",
                "temp_min",
                "precipitation",
                "event_count",
                "wildfire_count",
                "storm_count",
            ]
        ]
        .describe()
        .round(2),
        use_container_width=True,
    )

st.subheader("Column descriptions")
st.dataframe(column_info, use_container_width=True, hide_index=True)

st.header("3. Visual Storytelling")

time_series = (
    filtered.groupby("date", as_index=False)
    .agg(event_count=("event_count", "sum"), precipitation=("precipitation", "mean"))
    .melt("date", var_name="metric", value_name="value")
)

time_chart = (
    alt.Chart(time_series)
    .mark_line(point=True)
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("value:Q", title="Value"),
        color=alt.Color("metric:N", title="Metric"),
        tooltip=["date:T", "metric:N", alt.Tooltip("value:Q", format=".2f")],
    )
    .properties(height=320, title="Visual story overview: daily event counts and precipitation over time")
)

boxplot = (
    alt.Chart(filtered)
    .mark_boxplot(size=45)
    .encode(
        x=alt.X("event_label:N", title="Event-day group"),
        y=alt.Y("precipitation:Q", title="Precipitation (mm)"),
        color=alt.Color("event_label:N", legend=None),
        tooltip=["event_label:N", alt.Tooltip("precipitation:Q", format=".2f")],
    )
    .properties(height=320, title="Welch two-sample t-test chart: precipitation on event vs non-event days")
)

chi_source = (
    filtered.groupby(["rain_label", "event_label"], as_index=False)
    .size()
    .rename(columns={"size": "count"})
)

bar_chart = (
    alt.Chart(chi_source)
    .mark_bar()
    .encode(
        x=alt.X("rain_label:N", title="Rain group"),
        y=alt.Y("count:Q", title="Number of days"),
        color=alt.Color("event_label:N", title="Event-day status"),
        tooltip=["rain_label:N", "event_label:N", "count:Q"],
    )
    .properties(height=320, title="Chi-square test chart: rainy-day and event-day counts")
)

scatter = (
    alt.Chart(filtered)
    .mark_circle(size=80, opacity=0.65)
    .encode(
        x=alt.X("precipitation:Q", title="Precipitation (mm)"),
        y=alt.Y("event_count:Q", title="Event count"),
        color=alt.Color("holiday_label:N", title="Holiday group"),
        tooltip=[
            "date:T",
            alt.Tooltip("precipitation:Q", format=".2f"),
            alt.Tooltip("event_count:Q", format=".0f"),
            "holiday_label:N",
        ],
    )
    .properties(height=320, title="Spearman correlation chart: precipitation vs event count")
)

chart_col_1, chart_col_2 = st.columns(2)
chart_col_1.altair_chart(time_chart, use_container_width=True)
chart_col_2.altair_chart(boxplot, use_container_width=True)
chart_col_1.caption("Primary story chart. Supports the overall data narrative and trend context.")
chart_col_2.caption("Supports the Welch two-sample t-test comparing precipitation on event vs non-event days.")

chart_col_3, chart_col_4 = st.columns(2)
chart_col_3.altair_chart(bar_chart, use_container_width=True)
chart_col_4.altair_chart(scatter, use_container_width=True)
chart_col_3.caption("Supports the chi-square test of independence between rainy-day status and event-day status.")
chart_col_4.caption("Supports the Spearman correlation analysis between precipitation and event count.")

st.caption("The one-sample t-test is motivated by the precipitation summary itself, and the variance comparison is motivated by the holiday-group spread in the hypothesis-testing section.")

st.caption(
    """
These charts motivate the formal tests below: the boxplot supports the two-sample t-test,
the grouped bar chart supports the chi-square test, and the scatterplot supports the
correlation analysis.
"""
)

st.header("4. Hypothesis Testing")

one_sample_stat, one_sample_p = safe_ttest_1samp(filtered["precipitation"], popmean=0.0)
event_precip = filtered.loc[filtered["event_day"] == 1, "precipitation"]
non_event_precip = filtered.loc[filtered["event_day"] == 0, "precipitation"]
two_sample_stat, two_sample_p = safe_ttest_ind(event_precip, non_event_precip)

chi_table = pd.crosstab(filtered["rain_label"], filtered["event_label"])
chi_stat, chi_p, chi_dof, expected_df = safe_chi_square(chi_table)

holiday_precip = filtered.loc[filtered["holiday_flag"] == 1, "precipitation"]
non_holiday_precip = filtered.loc[filtered["holiday_flag"] == 0, "precipitation"]
levene_stat, levene_p = safe_levene(holiday_precip, non_holiday_precip)

spearman_r, spearman_p = safe_spearman(filtered["precipitation"], filtered["event_count"])

st.markdown("**Choose an analysis**")
analysis_choice = st.selectbox(
    "Choose an analysis",
    [
        "One-sample t-test",
        "Two-sample t-test",
        "Chi-square test of independence",
        "Variance comparison",
        "Spearman correlation",
    ],
    label_visibility="collapsed",
)

if analysis_choice == "One-sample t-test":
    one_sample_chart_data = pd.DataFrame(
        {
            "group": ["Observed mean", "Reference value"],
            "value": [filtered["precipitation"].mean(), 0.0],
        }
    )

    one_sample_chart = (
        alt.Chart(one_sample_chart_data)
        .mark_bar()
        .encode(
            x=alt.X("group:N", title=None),
            y=alt.Y("value:Q", title="Precipitation (mm)"),
            color=alt.Color("group:N", legend=None),
            tooltip=["group:N", alt.Tooltip("value:Q", format=".2f")],
        )
        .properties(height=320, title="One-sample t-test chart: observed mean precipitation vs 0 mm")
    )

    chart_col, test_col = st.columns(2)
    with chart_col:
        st.altair_chart(one_sample_chart, use_container_width=True)
    with test_col:
        render_test_result(
            title="One-sample t-test: mean precipitation vs 0 mm",
            hypotheses=[
                "Null hypothesis: The mean daily precipitation is 0 mm.",
                "Alternative hypothesis: The mean daily precipitation is different from 0 mm.",
            ],
            stat_label="t-statistic",
            stat_value=one_sample_stat,
            p_value=one_sample_p,
            explanation="""
Why this fits: precipitation is a continuous variable, and the test checks whether its mean
differs from a reference value. This is mainly a calibration-style test that shows the data
has measurable rainfall rather than staying centered at zero.
""",
            interpretation="""
Plain-language interpretation: if the p-value is small, the average day in the filtered
sample is not a zero-rainfall day. This does not say anything about events yet, but it helps
establish that precipitation varies enough to support later comparisons.
""",
            extra_lines=[f"Observed mean precipitation: {filtered['precipitation'].mean():.2f} mm"],
        )

elif analysis_choice == "Two-sample t-test":
    two_sample_chart = (
        alt.Chart(filtered)
        .mark_boxplot(size=45)
        .encode(
            x=alt.X("event_label:N", title="Event-day group"),
            y=alt.Y("precipitation:Q", title="Precipitation (mm)"),
            color=alt.Color("event_label:N", legend=None),
            tooltip=["event_label:N", alt.Tooltip("precipitation:Q", format=".2f")],
        )
        .properties(height=320, title="Welch two-sample t-test chart: precipitation on event vs non-event days")
    )

    chart_col, test_col = st.columns(2)
    with chart_col:
        st.altair_chart(two_sample_chart, use_container_width=True)
    with test_col:
        render_test_result(
            title="Welch two-sample t-test: precipitation on event vs non-event days",
            hypotheses=[
                "Null hypothesis: Mean precipitation is the same on event days and non-event days.",
                "Alternative hypothesis: Mean precipitation differs between event days and non-event days.",
            ],
            stat_label="t-statistic",
            stat_value=two_sample_stat,
            p_value=two_sample_p,
            explanation="""
Why this fits: precipitation is continuous and `event_day` creates two independent groups.
Welch's version is used because the groups may have different variances and different sizes.
""",
            interpretation="""
Plain-language interpretation: this tells us whether wetter or drier conditions tend to be
associated with days that contain at least one NASA event in the filtered sample.
""",
            extra_lines=[
                f"Event-day mean precipitation: {event_precip.mean():.2f} mm"
                if len(event_precip)
                else "Event-day mean precipitation: N/A",
                f"Non-event-day mean precipitation: {non_event_precip.mean():.2f} mm"
                if len(non_event_precip)
                else "Non-event-day mean precipitation: N/A",
            ],
        )

elif analysis_choice == "Chi-square test of independence":
    chi_chart = (
        alt.Chart(chi_source)
        .mark_bar()
        .encode(
            x=alt.X("rain_label:N", title="Rain group"),
            y=alt.Y("count:Q", title="Number of days"),
            color=alt.Color("event_label:N", title="Event-day status"),
            tooltip=["rain_label:N", "event_label:N", "count:Q"],
        )
        .properties(height=320, title="Chi-square test chart: observed rainy-day and event-day counts")
    )

    chart_col, test_col = st.columns(2)
    with chart_col:
        st.altair_chart(chi_chart, use_container_width=True)
        st.dataframe(chi_table, use_container_width=True)
    with test_col:
        extra_lines = [f"Degrees of freedom: {chi_dof}"]
        if not expected_df.empty:
            extra_lines.append(
                f"Minimum expected cell count: {expected_df.min().min():.2f}"
            )
        render_test_result(
            title="Chi-square test: event day vs rainy-day status",
            hypotheses=[
                "Null hypothesis: `event_day` is independent of `rainy_day`.",
                "Alternative hypothesis: `event_day` and `rainy_day` are associated.",
            ],
            stat_label="Chi-square statistic",
            stat_value=chi_stat,
            p_value=chi_p,
            explanation="""
Why this fits: both variables are categorical, and the question is whether event-day
frequency changes across rainy and non-rainy dates. The key assumption is that expected
cell counts are large enough for the chi-square approximation to be reasonable.
""",
            interpretation="""
Plain-language interpretation: a small p-value suggests that event-day frequency is not
distributed the same way on rainy and non-rainy days. That would still be an association,
not evidence that rainy weather directly causes events.
""",
            extra_lines=extra_lines,
        )
        if not expected_df.empty:
            st.caption("Expected counts under the null hypothesis")
            st.dataframe(expected_df.round(2), use_container_width=True)

elif analysis_choice == "Variance comparison":
    variance_chart_data = pd.DataFrame(
        {
            "group": ["Holiday", "Non-holiday"],
            "variance": [
                holiday_precip.var(ddof=1) if len(holiday_precip) > 1 else float("nan"),
                non_holiday_precip.var(ddof=1) if len(non_holiday_precip) > 1 else float("nan"),
            ],
        }
    )

    variance_chart = (
        alt.Chart(variance_chart_data)
        .mark_bar()
        .encode(
            x=alt.X("group:N", title="Group"),
            y=alt.Y("variance:Q", title="Sample variance"),
            color=alt.Color("group:N", legend=None),
            tooltip=["group:N", alt.Tooltip("variance:Q", format=".2f")],
        )
        .properties(height=320, title="Variance comparison chart: precipitation variance by holiday status")
    )

    chart_col, test_col = st.columns(2)
    with chart_col:
        st.altair_chart(variance_chart, use_container_width=True)
    with test_col:
        render_test_result(
            title="Levene variance test: precipitation variability on holiday vs non-holiday days",
            hypotheses=[
                "Null hypothesis: Precipitation variance is the same on holiday and non-holiday days.",
                "Alternative hypothesis: Precipitation variance differs between the two groups.",
            ],
            stat_label="Levene statistic",
            stat_value=levene_stat,
            p_value=levene_p,
            explanation="""
Why this fits: the assignment asks for a variance comparison, and Levene's test is a
statistically justified choice because it is more robust than the classic F-test when data
is skewed or not perfectly normal.
""",
            interpretation="""
Plain-language interpretation: this checks whether rainfall is similarly stable across
holiday and non-holiday dates, or whether one group shows more spread and volatility.
""",
            extra_lines=[
                f"Holiday precipitation variance: {holiday_precip.var(ddof=1):.2f}"
                if len(holiday_precip) > 1
                else "Holiday precipitation variance: N/A",
                f"Non-holiday precipitation variance: {non_holiday_precip.var(ddof=1):.2f}"
                if len(non_holiday_precip) > 1
                else "Non-holiday precipitation variance: N/A",
            ],
        )

else:
    corr_chart = (
        alt.Chart(filtered)
        .mark_circle(size=80, opacity=0.65)
        .encode(
            x=alt.X("precipitation:Q", title="Precipitation (mm)"),
            y=alt.Y("event_count:Q", title="Event count"),
            color=alt.Color("holiday_label:N", title="Holiday group"),
            tooltip=[
                "date:T",
                alt.Tooltip("precipitation:Q", format=".2f"),
                alt.Tooltip("event_count:Q", format=".0f"),
                "holiday_label:N",
            ],
        )
        .properties(height=320, title="Spearman correlation chart: precipitation and event-count relationship")
    )

    chart_col, test_col = st.columns(2)
    with chart_col:
        st.altair_chart(corr_chart, use_container_width=True)
    with test_col:
        render_test_result(
            title="Spearman correlation: precipitation vs event count",
            hypotheses=[
                "Null hypothesis: There is no monotonic association between precipitation and event count.",
                "Alternative hypothesis: There is a monotonic association between precipitation and event count.",
            ],
            stat_label="Spearman rho",
            stat_value=spearman_r,
            p_value=spearman_p,
            explanation="""
Why this fits: both variables are quantitative, but event counts are discrete and may not
follow a linear relationship. Spearman correlation is a safer choice when monotonic
association matters more than strict linearity.
""",
            interpretation="""
Plain-language interpretation: this measures whether days with more rainfall also tend to
have higher or lower event counts. Even a significant correlation does not establish a
causal mechanism.
""",
        )

st.header("5. Reflection and Limitations")
st.markdown(
    """
- The dataset is joined at the daily level, so any within-day timing is lost.
- NASA EONET event counts reflect recorded events, which may be influenced by reporting and category definitions.
- Holiday status is a useful grouping feature, but it should be treated as contextual rather than causal.
- T-tests assume reasonably independent daily observations, and the chi-square test depends on adequate expected counts.
- Statistical significance does not automatically imply a large practical effect or a real-world mechanism.
"""
)
