"""Streamlit dashboard: financial ratios of Brazilian listed retailers.

Input: data/processed/ratios.csv (created by src/compute_ratios.py)
Run from the project root:  streamlit run app.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_PATH = Path("data") / "processed" / "ratios.csv"

# Each company keeps the same color, whatever is selected
COMPANY_COLORS = {
    "Magazine Luiza": "#2a78d6",
    "Lojas Renner": "#eb6834",
    "Grupo SBF": "#1baf7a",
    "C&A": "#eda100",
}

RATIOS = {
    "current_ratio": {
        "label": "Current ratio",
        "is_percent": False,
        "higher_is_better": True,
        "help": "Current assets / current liabilities. Ability to pay short-term obligations.",
    },
    "gross_margin": {
        "label": "Gross margin",
        "is_percent": True,
        "higher_is_better": True,
        "help": "Gross profit / net revenue. What is left after the cost of goods sold.",
    },
    "operating_margin": {
        "label": "Operating margin",
        "is_percent": True,
        "higher_is_better": True,
        "help": "Operating income (before financial result and taxes) / net revenue.",
    },
    "net_margin": {
        "label": "Net margin",
        "is_percent": True,
        "higher_is_better": True,
        "help": "Net income / net revenue.",
    },
    "roe": {
        "label": "ROE",
        "is_percent": True,
        "higher_is_better": True,
        "help": "Net income / shareholders' equity (end of year).",
    },
    "debt_ratio": {
        "label": "Debt ratio",
        "is_percent": True,
        "higher_is_better": False,
        "help": "Total liabilities / total assets. Share of assets financed by third parties.",
    },
}

# Points that need context: (company, year, ratios affected) -> note
NOTES = [
    {
        "company": "C&A",
        "year": 2021,
        "ratios": ["net_margin", "roe"],
        "text": (
            "**C&A 2021:** net income came almost entirely from a one-off tax gain "
            "(R$ 311 million deferred tax asset after the STF ruling on IRPJ/CSLL over Selic "
            "interest on tax refunds). According to the management report, C&A would have "
            "reported a net loss without it."
        ),
    },
]


@st.cache_data
def load_ratios():
    return pd.read_csv(DATA_PATH)


def format_value(value, is_percent):
    if is_percent:
        return f"{value:.1%}"
    return f"{value:.2f}x"


def format_change(change, is_percent):
    if is_percent:
        return f"{change * 100:+.1f} p.p."
    return f"{change:+.2f}x"


def line_chart(data, ratio, is_percent):
    """Line chart of one ratio over time, one line per company, with hover tooltips."""
    axis_format = ".0%" if is_percent else ".2f"
    tooltip_format = ".1%" if is_percent else ".2f"

    color_scale = alt.Scale(domain=list(COMPANY_COLORS.keys()), range=list(COMPANY_COLORS.values()))

    lines = (
        alt.Chart(data)
        .mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=2)
        .encode(
            x=alt.X("YEAR:O", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{ratio}:Q", title=None, axis=alt.Axis(format=axis_format)),
            color=alt.Color("COMPANY:N", scale=color_scale, legend=alt.Legend(title=None, orient="top")),
            tooltip=[
                alt.Tooltip("COMPANY:N", title="Company"),
                alt.Tooltip("YEAR:O", title="Year"),
                alt.Tooltip(f"{ratio}:Q", title=RATIOS[ratio]["label"], format=tooltip_format),
            ],
        )
    )

    # Zero line, only when there are negative values (losses)
    if data[ratio].min() < 0:
        zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#898781").encode(y="y:Q")
        return (zero + lines).properties(height=380)

    return lines.properties(height=380)


# ---------- Page ----------

st.set_page_config(page_title="Brazilian Retail Financial Analysis", layout="wide")

st.title("Brazilian Retail Financial Analysis")
st.caption(
    "Financial ratios of four listed Brazilian retailers, 2021-2025. "
    "Source: CVM open data (DFP, consolidated statements)."
)

ratios = load_ratios()

# Filters in one row
col_ratio, col_companies = st.columns([1, 2])
with col_ratio:
    ratio = st.selectbox(
        "Ratio",
        options=list(RATIOS.keys()),
        format_func=lambda key: RATIOS[key]["label"],
    )
with col_companies:
    companies = st.multiselect(
        "Companies",
        options=list(COMPANY_COLORS.keys()),
        default=list(COMPANY_COLORS.keys()),
    )

if not companies:
    st.warning("Select at least one company.")
    st.stop()

info = RATIOS[ratio]
selected = ratios[ratios["COMPANY"].isin(companies)]

st.caption(info["help"])

# Latest year, with change versus the previous year
last_year = selected["YEAR"].max()
st.subheader(f"{info['label']} in {last_year}")

metric_columns = st.columns(len(companies))
for column, company in zip(metric_columns, companies):
    company_data = selected[selected["COMPANY"] == company].set_index("YEAR")
    current = company_data.loc[last_year, ratio]
    previous = company_data.loc[last_year - 1, ratio]
    column.metric(
        label=company,
        value=format_value(current, info["is_percent"]),
        delta=format_change(current - previous, info["is_percent"]),
        delta_color="normal" if info["higher_is_better"] else "inverse",
    )

# Chart
st.subheader("Evolution")
st.altair_chart(line_chart(selected, ratio, info["is_percent"]), width="stretch")

# Context notes for the points shown
for note in NOTES:
    if ratio in note["ratios"] and note["company"] in companies:
        st.info(note["text"])

# Table view of the same data
with st.expander("See the data as a table"):
    table = selected.pivot(index="COMPANY", columns="YEAR", values=ratio)
    if info["is_percent"]:
        table = (table * 100).round(1)
        st.caption("Values in %.")
    else:
        table = table.round(2)
    st.dataframe(table)

st.divider()
st.caption(
    "Net income and equity include non-controlling interests. ROE uses end-of-year equity. "
    "Values were validated against the DFP filed with CVM (see the README)."
)
