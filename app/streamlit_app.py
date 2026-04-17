from pathlib import Path

import altair as alt

alt.data_transformers.disable_max_rows()
import pandas as pd
import streamlit as st
from scipy import stats


st.set_page_config(
    page_title="Statistical Analysis of Weather and Natural Events",
    page_icon="",
    layout="wide",
)


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "gold" / "nasa_weather_gold.csv"
HOLIDAY_SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "silver" / "holidays" / "daily_holidays.csv"
)


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


@st.cache_data
def load_holiday_source() -> pd.DataFrame:
    holiday_df = pd.read_csv(HOLIDAY_SOURCE_PATH)
    holiday_df["date"] = pd.to_datetime(holiday_df["date"])
    return holiday_df.sort_values("date").reset_index(drop=True)


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


def hypothesis_decision(p_value: float) -> str:
    if pd.isna(p_value):
        return "No decision"
    if p_value < 0.05:
        return "Reject H0"
    return "Fail to reject H0"


def render_summary_strip(items: list[tuple[str, str]]) -> None:
    cells = "".join(
        f"""
        <div class="summary-cell">
            <div class="summary-label">{label}</div>
            <div class="summary-value">{value}</div>
        </div>
        """
        for label, value in items
    )
    st.markdown(
        f"""
        <div class="summary-strip">
            {cells}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_callout_card(kind: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="callout-card callout-{kind}">
            <div class="callout-title">{title}</div>
            <div class="callout-body">{body.strip()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(label: str) -> None:
    st.markdown(f"""<div class="section-label">{label}</div>""", unsafe_allow_html=True)


def render_hypotheses_block(hypotheses: list[str]) -> None:
    items = "".join(f"""<div class="hypothesis-line">{line}</div>""" for line in hypotheses)
    st.markdown(
        f"""
        <div class="hypothesis-block">
            {items}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_detail_lines(lines: list[str]) -> None:
    items = "".join(f"""<div class="detail-line">{line}</div>""" for line in lines)
    st.markdown(
        f"""
        <div class="detail-block">
            {items}
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_table(
    df: pd.DataFrame, precision: int = 2, hide_index: bool = False
) -> "pd.io.formats.style.Styler":
    styled = (
        df.style.format(precision=precision, na_rep="N/A")
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        ("background-color", "#18263d"),
                        ("color", "#d6e7ff"),
                        ("font-weight", "700"),
                        ("border", "1px solid #2b3c58"),
                        ("text-transform", "uppercase"),
                        ("font-size", "0.78rem"),
                        ("letter-spacing", "0.04em"),
                    ],
                },
                {
                    "selector": "thead th:first-child",
                    "props": [
                        ("background-color", "#213250"),
                        ("color", "#f4f8ff"),
                    ],
                },
                {
                    "selector": "tbody td",
                    "props": [
                        ("border", "1px solid #243348"),
                        ("padding", "0.5rem 0.6rem"),
                        ("color", "#d9e3f0"),
                    ],
                },
                {
                    "selector": "tbody tr:nth-child(even)",
                    "props": [("background-color", "#0f1a2b")],
                },
                {
                    "selector": "tbody tr:nth-child(odd)",
                    "props": [("background-color", "#132033")],
                },
                {
                    "selector": "tbody tr:hover td",
                    "props": [("background-color", "#1a2a40")],
                },
                {
                    "selector": "table",
                    "props": [
                        ("border-collapse", "collapse"),
                        ("border", "1px solid #243348"),
                        ("border-radius", "10px"),
                        ("overflow", "hidden"),
                    ],
                },
            ]
        )
    )
    if hide_index:
        styled = styled.hide(axis="index")
    return styled


def style_sample_table(df: pd.DataFrame, precision: int = 2) -> "pd.io.formats.style.Styler":
    display_df = df.copy()
    if "date" in display_df.columns:
        display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%Y-%m-%d")

    return display_df.style.format(precision=precision, na_rep="N/A").set_table_styles(
        [
            {
                "selector": "thead th",
                "props": [
                    ("background-color", "#18263d"),
                    ("color", "#d6e7ff"),
                    ("font-weight", "600"),
                    ("border", "1px solid #2b3c58"),
                    ("font-size", "0.8rem"),
                    ("text-transform", "none"),
                    ("white-space", "nowrap"),
                ],
            },
            {
                "selector": "thead th.col_heading.level0.col0",
                "props": [
                    ("min-width", "96px"),
                    ("width", "96px"),
                    ("background-color", "#213250"),
                    ("color", "#f4f8ff"),
                ],
            },
            {
                "selector": "tbody td, tbody th",
                "props": [
                    ("border", "1px solid #243348"),
                    ("padding", "0.34rem 0.42rem"),
                    ("color", "#d9e3f0"),
                    ("font-size", "0.82rem"),
                    ("background-color", "#101a2b"),
                    ("white-space", "nowrap"),
                ],
            },
            {
                "selector": "tbody th",
                "props": [
                    ("font-weight", "500"),
                    ("color", "#aebed2"),
                    ("background-color", "#142136"),
                ],
            },
            {
                "selector": "tbody td.col0",
                "props": [
                    ("min-width", "96px"),
                    ("width", "96px"),
                    ("white-space", "nowrap"),
                ],
            },
            {
                "selector": "tbody td",
                "props": [("max-width", "92px")],
            },
            {
                "selector": "tbody tr:nth-child(even) td",
                "props": [("background-color", "#0f1a2b")],
            },
            {
                "selector": "tbody tr:nth-child(odd) td",
                "props": [("background-color", "#132033")],
            },
            {
                "selector": "tbody tr:hover td, tbody tr:hover th",
                "props": [("background-color", "#1a2a40")],
            },
            {
                "selector": "table",
                "props": [
                    ("border-collapse", "collapse"),
                    ("border", "1px solid #243348"),
                    ("border-radius", "10px"),
                    ("overflow", "hidden"),
                    ("width", "auto"),
                ],
            },
        ]
    )


def render_styled_table(styled: "pd.io.formats.style.Styler") -> None:
    st.markdown(
        f'<div class="table-wrap">{styled.to_html()}</div>',
        unsafe_allow_html=True,
    )


CHART_COLORS = {
    "blue": "#59d0ff",
    "blue_soft": "#7bb0ff",
    "green": "#56e39f",
    "amber": "#ffbf69",
    "red": "#ff7a90",
    "violet": "#b99cff",
}


def style_altair_chart(chart: alt.Chart) -> alt.Chart:
    return (
        chart.configure(
            background="#0b1626",
            padding={"left": 12, "right": 12, "top": 12, "bottom": 12},
        )
        .configure_view(stroke="#22344d", cornerRadius=16)
        .configure_axis(
            domainColor="#314863",
            gridColor="#1f3148",
            labelColor="#dbe7f5",
            tickColor="#314863",
            titleColor="#f3f8ff",
            titleFontSize=13,
            labelFontSize=11,
        )
        .configure_title(
            color="#f3f8ff",
            fontSize=16,
            anchor="start",
            offset=12,
        )
        .configure_legend(
            titleColor="#f3f8ff",
            labelColor="#dbe7f5",
            orient="top",
            padding=8,
            cornerRadius=10,
            fillColor="#0f1b2d",
            strokeColor="#22344d",
        )
    )


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
    analysis_question: str,
    hypotheses: list[str],
    stat_label: str,
    stat_value: float,
    p_value: float,
    explanation: str,
    assumptions: str,
    interpretation: str,
    summary_items: list[tuple[str, str]] | None = None,
    extra_lines: list[str] | None = None,
) -> None:
    st.subheader(title)
    st.markdown(f"**Analysis question**  \n{analysis_question}")
    render_section_label("Hypotheses")
    render_hypotheses_block(hypotheses)
    summary_strip_items = []
    if summary_items:
        summary_strip_items.extend(summary_items)
    summary_strip_items.extend(
        [
            (stat_label, f"{stat_value:.3f}" if pd.notna(stat_value) else "N/A"),
            ("p-value", fmt_p_value(p_value)),
            ("Result", hypothesis_decision(p_value)),
        ]
    )
    render_section_label("Supporting Details")
    render_summary_strip(summary_strip_items)
    if extra_lines:
        render_detail_lines(extra_lines)
    render_callout_card("blue", "Why This Test Fits", explanation)
    render_callout_card("green", "Assumptions Check", assumptions)
    render_callout_card("amber", "Plain-Language Caution", interpretation)
    st.success(describe_significance(p_value))


df = load_data()
holiday_source = load_holiday_source()

st.markdown(
    """
    <h1 style="text-align: center; margin-bottom: 0.25rem;">
        Statistical Analysis of Weather and Natural Events
    </h1>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
    :root {
        --bg-main: #07111f;
        --bg-surface: rgba(11, 22, 38, 0.88);
        --bg-surface-strong: #0f1b2d;
        --bg-surface-soft: #13233a;
        --border-color: rgba(122, 163, 255, 0.16);
        --text-main: #ecf3ff;
        --text-muted: #9cb1c9;
        --accent-blue: #7bb0ff;
        --accent-cyan: #59d0ff;
        --accent-green: #56e39f;
        --accent-amber: #ffbf69;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(89, 208, 255, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(123, 176, 255, 0.16), transparent 24%),
            linear-gradient(180deg, #07111f 0%, #0a1626 45%, #08111d 100%);
        color: var(--text-main);
    }
    [data-testid="stAppViewContainer"] {
        background: transparent;
    }
    [data-testid="stHeader"] {
        background: rgba(7, 17, 31, 0.72);
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(11, 22, 38, 0.97) 0%, rgba(8, 16, 28, 0.96) 100%);
        border-right: 1px solid var(--border-color);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stDateInput,
    [data-testid="stSidebar"] .stSelectbox {
        color: var(--text-main);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, h4, p, li, label, .stMarkdown, .stCaption {
        color: var(--text-main);
    }
    h1 {
        color: #f5f9ff;
        text-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stDateInput > div > div {
        background: rgba(15, 27, 45, 0.95);
        border: 1px solid var(--border-color);
        color: var(--text-main);
    }
    div[data-baseweb="select"] input,
    div[data-baseweb="input"] input {
        color: var(--text-main) !important;
    }
    .stAlert {
        background: rgba(14, 25, 41, 0.92);
        border: 1px solid var(--border-color);
    }
    .stExpander {
        background: rgba(11, 22, 38, 0.8);
        border: 1px solid var(--border-color);
        border-radius: 16px;
    }
    .stDataFrame, .stTable {
        border-radius: 14px;
        overflow: visible;
    }
    [data-testid="stDataFrame"],
    [data-testid="stDataFrameResizable"],
    [data-testid="stArrowVegaLiteChart"] {
        overflow: visible !important;
    }
    [data-testid="stArrowVegaLiteChart"] + div,
    .vega-embed,
    .vega-embed summary {
        overflow: visible !important;
    }
    .summary-strip {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 0.75rem;
        padding: 1rem 1.15rem;
        margin: 0.3rem 0 0.75rem 0;
        border-left: 6px solid var(--accent-cyan);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        border-radius: 16px;
        background: linear-gradient(180deg, rgba(15, 27, 45, 0.95) 0%, rgba(10, 20, 35, 0.95) 100%);
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.24);
        backdrop-filter: blur(10px);
    }
    .summary-cell {
        text-align: center;
    }
    .summary-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.2rem;
    }
    .summary-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f3f8ff;
        line-height: 1.2;
    }
    .section-label {
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        color: #b5c8df;
        margin: 1rem 0 0.45rem 0;
    }
    .hypothesis-block, .detail-block {
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin: 0.2rem 0 0.6rem 0;
        background: linear-gradient(180deg, rgba(12, 24, 40, 0.92) 0%, rgba(9, 18, 31, 0.92) 100%);
        border: 1px solid var(--border-color);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.16);
    }
    .hypothesis-line, .detail-line {
        font-size: 1rem;
        line-height: 1.65;
        color: #d9e3f0;
    }
    .hypothesis-line + .hypothesis-line,
    .detail-line + .detail-line {
        margin-top: 0.7rem;
        padding-top: 0.7rem;
        border-top: 1px solid rgba(156, 177, 201, 0.16);
    }
    .callout-card {
        border-radius: 16px;
        padding: 1rem 1.2rem 1.05rem 1.2rem;
        margin: 0.8rem 0;
        border-left: 5px solid;
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        box-shadow: 0 18px 38px rgba(0, 0, 0, 0.2);
    }
    .callout-title {
        font-size: 0.92rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.5rem;
    }
    .callout-body {
        font-size: 1.02rem;
        line-height: 1.7;
        color: #d9e3f0;
    }
    .callout-blue {
        background: linear-gradient(180deg, rgba(19, 40, 68, 0.96) 0%, rgba(12, 28, 47, 0.96) 100%);
        border-left-color: var(--accent-blue);
    }
    .callout-blue .callout-title {
        color: #cfe1ff;
    }
    .callout-green {
        background: linear-gradient(180deg, rgba(16, 46, 40, 0.96) 0%, rgba(10, 31, 27, 0.96) 100%);
        border-left-color: var(--accent-green);
    }
    .callout-green .callout-title {
        color: #c7f8df;
    }
    .callout-amber {
        background: linear-gradient(180deg, rgba(63, 42, 16, 0.96) 0%, rgba(41, 27, 10, 0.96) 100%);
        border-left-color: var(--accent-amber);
    }
    .callout-amber .callout-title {
        color: #ffe0b0;
    }
    .table-wrap {
        width: 100%;
        overflow-x: auto;
        margin: 0.2rem 0 0.8rem 0;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        background: rgba(11, 22, 38, 0.78);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.18);
    }
    .table-wrap table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.92rem;
        border-radius: 16px;
        overflow: hidden;
    }
    .table-wrap th.col_heading,
    .table-wrap th.blank,
    .table-wrap th.index_name {
        position: sticky;
        top: 0;
        z-index: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
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

render_summary_strip(
    [
        ("Rows in view", f"{len(filtered):,}"),
        ("Event days", f"{int(filtered['event_day'].sum()):,}"),
        ("Holiday days", f"{int(filtered['holiday_flag'].sum()):,}"),
        ("Mean precipitation", f"{filtered['precipitation'].mean():.2f} mm"),
    ]
)

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

st.subheader("Sample rows")
render_styled_table(style_sample_table(filtered.head(10), precision=2))

st.subheader("Summary statistics")
render_styled_table(
    style_table(
        filtered[
            [
                "temp_max",
                "temp_min",
                "precipitation",
                "event_count",
                "wildfire_count",
                "storm_count",
                "holiday_flag",
            ]
        ].describe(),
        precision=2,
    )
)

st.subheader("Column descriptions")
render_styled_table(style_table(column_info, precision=0, hide_index=True))

with st.expander("How the final dataset was prepared"):
    st.markdown(
        """
        1. Open-Meteo JSON was flattened into daily weather rows.
        2. NASA EONET event geometry timestamps were aggregated into daily counts.
        3. The holiday source was cleaned into one row per holiday date.
        4. All three sources were joined on `date`.
        5. Missing event values were filled with 0, and new flags such as `event_day`, `rainy_day`,
           `holiday_flag`, and `holiday_or_weekend` were derived for analysis.
        """
    )
    st.caption("Preview of the final prepared dataset")
    st.dataframe(filtered.head(10), use_container_width=True, hide_index=True)
    st.caption("Holiday source used during the preparation step")
    st.dataframe(holiday_source, use_container_width=True, hide_index=True)

st.header("3. Visual Storytelling")

time_series = (
    filtered.groupby("date", as_index=False)
    .agg(event_count=("event_count", "sum"), precipitation=("precipitation", "mean"))
    .melt("date", var_name="metric", value_name="value")
)

time_chart = (
    alt.Chart(time_series)
    .mark_line(point={"filled": True, "size": 70}, strokeWidth=3)
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("value:Q", title="Value"),
        color=alt.Color(
            "metric:N",
            title="Metric",
            scale=alt.Scale(
                domain=["event_count", "precipitation"],
                range=[CHART_COLORS["blue"], CHART_COLORS["amber"]],
            ),
        ),
        tooltip=["date:T", "metric:N", alt.Tooltip("value:Q", format=".2f")],
    )
    .properties(height=320, title="Visual story overview: daily event counts and precipitation over time")
)
time_chart = style_altair_chart(time_chart)

boxplot = (
    alt.Chart(filtered)
    .mark_boxplot(size=45)
    .encode(
        x=alt.X("event_label:N", title="Event-day group"),
        y=alt.Y("precipitation:Q", title="Precipitation (mm)"),
        color=alt.Color(
            "event_label:N",
            legend=None,
            scale=alt.Scale(
                domain=["No event day", "Event day"],
                range=[CHART_COLORS["blue_soft"], CHART_COLORS["green"]],
            ),
        ),
        tooltip=["event_label:N", alt.Tooltip("precipitation:Q", format=".2f")],
    )
    .properties(height=320, title="Welch two-sample t-test chart: precipitation on event vs non-event days")
)
boxplot = style_altair_chart(boxplot)

chi_source = (
    filtered.groupby(["rain_label", "event_label"], as_index=False)
    .size()
    .rename(columns={"size": "count"})
)

bar_chart = (
    alt.Chart(chi_source)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("rain_label:N", title="Rain group"),
        y=alt.Y("count:Q", title="Number of days"),
        color=alt.Color(
            "event_label:N",
            title="Event-day status",
            scale=alt.Scale(
                domain=["No event day", "Event day"],
                range=[CHART_COLORS["violet"], CHART_COLORS["blue"]],
            ),
        ),
        tooltip=["rain_label:N", "event_label:N", "count:Q"],
    )
    .properties(height=320, title="Chi-square test chart: rainy-day and event-day counts")
)
bar_chart = style_altair_chart(bar_chart)

scatter = (
    alt.Chart(filtered)
    .mark_circle(size=90, opacity=0.72)
    .encode(
        x=alt.X("precipitation:Q", title="Precipitation (mm)"),
        y=alt.Y("event_count:Q", title="Event count"),
        color=alt.Color(
            "holiday_label:N",
            title="Holiday group",
            scale=alt.Scale(
                domain=["Non-holiday", "Holiday"],
                range=[CHART_COLORS["blue_soft"], CHART_COLORS["amber"]],
            ),
        ),
        tooltip=[
            "date:T",
            alt.Tooltip("precipitation:Q", format=".2f"),
            alt.Tooltip("event_count:Q", format=".0f"),
            "holiday_label:N",
        ],
    )
    .properties(height=320, title="Spearman correlation chart: precipitation vs event count")
)
scatter = style_altair_chart(scatter)

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
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("group:N", title=None),
            y=alt.Y("value:Q", title="Precipitation (mm)"),
            color=alt.Color(
                "group:N",
                legend=None,
                scale=alt.Scale(
                    domain=["Observed mean", "Reference value"],
                    range=[CHART_COLORS["blue"], CHART_COLORS["violet"]],
                ),
            ),
            tooltip=["group:N", alt.Tooltip("value:Q", format=".2f")],
        )
        .properties(height=320, title="One-sample t-test chart: observed mean precipitation vs 0 mm")
    )
    one_sample_chart = style_altair_chart(one_sample_chart)

    st.altair_chart(one_sample_chart, use_container_width=True)
    render_test_result(
        title="One-sample t-test: mean precipitation vs 0 mm",
        analysis_question="Is the mean daily precipitation in the filtered sample different from 0 mm?",
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
        assumptions="""
The filtered sample should contain enough observations, and daily rows are treated as
reasonably independent for this comparison to be meaningful.
""",
        interpretation="""
This result only tells us whether average precipitation differs from 0 mm in the filtered
sample. It helps describe the rainfall pattern, but it does not answer the event question by itself.
""",
        summary_items=[
            ("Observed mean", f"{filtered['precipitation'].mean():.2f} mm"),
        ],
        extra_lines=[f"Observed mean precipitation: {filtered['precipitation'].mean():.2f} mm"],
    )

elif analysis_choice == "Two-sample t-test":
    two_sample_chart = (
        alt.Chart(filtered)
        .mark_boxplot(size=45)
        .encode(
            x=alt.X("event_label:N", title="Event-day group"),
            y=alt.Y("precipitation:Q", title="Precipitation (mm)"),
            color=alt.Color(
                "event_label:N",
                legend=None,
                scale=alt.Scale(
                    domain=["No event day", "Event day"],
                    range=[CHART_COLORS["blue_soft"], CHART_COLORS["green"]],
                ),
            ),
            tooltip=["event_label:N", alt.Tooltip("precipitation:Q", format=".2f")],
        )
        .properties(height=320, title="Welch two-sample t-test chart: precipitation on event vs non-event days")
    )
    two_sample_chart = style_altair_chart(two_sample_chart)

    st.altair_chart(two_sample_chart, use_container_width=True)
    render_test_result(
        title="Welch two-sample t-test: precipitation on event vs non-event days",
        analysis_question="Does mean precipitation differ between event days and non-event days?",
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
        assumptions="""
The two groups should be reasonably independent, and each group needs enough observations
for the mean comparison to be stable.
""",
        interpretation="""
This comparison shows whether precipitation differs across event and non-event days, but it
does not prove that rainfall causes natural events to occur.
""",
        summary_items=[
            ("Event mean", f"{event_precip.mean():.2f} mm" if len(event_precip) else "N/A"),
            (
                "Non-event mean",
                f"{non_event_precip.mean():.2f} mm" if len(non_event_precip) else "N/A",
            ),
        ],
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
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("rain_label:N", title="Rain group"),
            y=alt.Y("count:Q", title="Number of days"),
            color=alt.Color(
                "event_label:N",
                title="Event-day status",
                scale=alt.Scale(
                    domain=["No event day", "Event day"],
                    range=[CHART_COLORS["violet"], CHART_COLORS["blue"]],
                ),
            ),
            tooltip=["rain_label:N", "event_label:N", "count:Q"],
        )
        .properties(height=320, title="Chi-square test chart: observed rainy-day and event-day counts")
    )
    chi_chart = style_altair_chart(chi_chart)

    st.altair_chart(chi_chart, use_container_width=True)
    st.dataframe(chi_table, use_container_width=True)
    extra_lines = [f"Degrees of freedom: {chi_dof}"]
    if not expected_df.empty:
        extra_lines.append(
            f"Minimum expected cell count: {expected_df.min().min():.2f}"
        )
    render_test_result(
        title="Chi-square test: event day vs rainy-day status",
        analysis_question="Is the occurrence of a natural event associated with whether a day is rainy?",
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
        assumptions="""
Expected cell counts should be large enough in the filtered data, and each date should
contribute to only one rain-by-event category combination.
""",
        interpretation="""
Rainy-day status is a broad grouping and does not isolate storm timing, wildfire conditions,
or reporting differences. A significant result would still show association, not causation.
""",
        summary_items=[
            ("Degrees of freedom", str(chi_dof)),
            (
                "Min expected count",
                f"{expected_df.min().min():.2f}" if not expected_df.empty else "N/A",
            ),
        ],
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
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("group:N", title="Group"),
            y=alt.Y("variance:Q", title="Sample variance"),
            color=alt.Color(
                "group:N",
                legend=None,
                scale=alt.Scale(
                    domain=["Holiday", "Non-holiday"],
                    range=[CHART_COLORS["amber"], CHART_COLORS["blue_soft"]],
                ),
            ),
            tooltip=["group:N", alt.Tooltip("variance:Q", format=".2f")],
        )
        .properties(height=320, title="Variance comparison chart: precipitation variance by holiday status")
    )
    variance_chart = style_altair_chart(variance_chart)

    st.altair_chart(variance_chart, use_container_width=True)
    render_test_result(
        title="Levene variance test: precipitation variability on holiday vs non-holiday days",
        analysis_question="Is precipitation variability different on holiday versus non-holiday days?",
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
        assumptions="""
The holiday and non-holiday groups should be independent enough to compare spread, and each
group needs enough observations for a meaningful variance estimate.
""",
        interpretation="""
Holiday grouping adds context, but it does not isolate the many factors that can affect
precipitation variability from day to day.
""",
        summary_items=[
            (
                "Holiday variance",
                f"{holiday_precip.var(ddof=1):.2f}" if len(holiday_precip) > 1 else "N/A",
            ),
            (
                "Non-holiday variance",
                f"{non_holiday_precip.var(ddof=1):.2f}"
                if len(non_holiday_precip) > 1
                else "N/A",
            ),
        ],
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
        .mark_circle(size=90, opacity=0.72)
        .encode(
            x=alt.X("precipitation:Q", title="Precipitation (mm)"),
            y=alt.Y("event_count:Q", title="Event count"),
            color=alt.Color(
                "holiday_label:N",
                title="Holiday group",
                scale=alt.Scale(
                    domain=["Non-holiday", "Holiday"],
                    range=[CHART_COLORS["blue_soft"], CHART_COLORS["amber"]],
                ),
            ),
            tooltip=[
                "date:T",
                alt.Tooltip("precipitation:Q", format=".2f"),
                alt.Tooltip("event_count:Q", format=".0f"),
                "holiday_label:N",
            ],
        )
        .properties(height=320, title="Spearman correlation chart: precipitation and event-count relationship")
    )
    corr_chart = style_altair_chart(corr_chart)

    st.altair_chart(corr_chart, use_container_width=True)
    render_test_result(
        title="Spearman correlation: precipitation vs event count",
        analysis_question="Is precipitation associated with event count?",
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
        assumptions="""
The relationship should be interpretable at the daily level, and the variables need enough
variation for a correlation measure to be informative.
""",
        interpretation="""
Correlation summarizes co-movement, but it cannot show which variable drives the other, and
it can be influenced by seasonality or other omitted factors.
""",
        summary_items=[],
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
