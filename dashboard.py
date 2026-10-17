import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import re


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

RAW_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_PATH = (
    PROJECT_ROOT
    / "data"
    / "lake"
    / "processed"
    / "fact_sales.parquet"
)

LOG_PATH = PROJECT_ROOT / "logs" / "pipeline.log"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="E-Commerce DataForge",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DARK DATAFORGE STYLE
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0b0e14;
        color: #f5f7fa;
    }

    /* Main content */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1500px;
    }

    /* Titles */
    .hero-title {
        font-size: 42px;
        font-weight: 750;
        letter-spacing: -1px;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .hero-subtitle {
        font-size: 15px;
        color: #8b929f;
        margin-bottom: 28px;
    }

    /* Section titles */
    h1, h2, h3 {
        color: #f8fafc !important;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: #10141c;
        border: 1px solid #202633;
        border-radius: 12px;
        padding: 18px 20px;
        min-height: 120px;
    }

    div[data-testid="stMetric"] label {
        color: #a8b0bd !important;
        font-size: 14px !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 30px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        color: #4ade80 !important;
    }

    /* Cards */
    .info-card {
        background: #10141c;
        border: 1px solid #202633;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .info-title {
        color: #f8fafc;
        font-size: 17px;
        font-weight: 650;
        margin-bottom: 10px;
    }

    .info-text {
        color: #9ca3af;
        font-size: 14px;
        line-height: 1.7;
    }

    /* Status badges */
    .success-badge {
        display: inline-block;
        background: #12351f;
        color: #4ade80;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }

    .warning-badge {
        display: inline-block;
        background: #3b2d10;
        color: #fbbf24;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0e1118;
        border-right: 1px solid #202633;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #202633;
        border-radius: 10px;
    }

    /* Select box */
    div[data-baseweb="select"] > div {
        background-color: #171b24;
        border-color: #303746;
    }

    /* Divider */
    hr {
        border-color: #202633;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ANALYTICS IMPORT
# ============================================================

sys.path.append(str(PROJECT_ROOT / "src"))

from analytics import (
    get_total_metrics,
    get_monthly_revenue,
    get_top_categories,
    get_yearly_revenue,
    get_top_products,
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_raw_dataset(filename):

    path = RAW_PATH / filename

    return pd.read_csv(
        path,
        low_memory=False
    )


@st.cache_data
def load_processed_data():

    return pd.read_parquet(
        PROCESSED_PATH
    )


# ============================================================
# DATASET INFORMATION
# ============================================================

DATASETS = {
    "Orders": "olist_orders_dataset.csv",
    "Products": "olist_products_dataset.csv",
    "Reviews": "olist_order_reviews_dataset.csv",
    "Customers": "olist_customers_dataset.csv",
    "Order Items": "olist_order_items_dataset.csv",
    "Payments": "olist_order_payments_dataset.csv",
    "Sellers": "olist_sellers_dataset.csv",
    "Geolocation": "olist_geolocation_dataset.csv",
}


# ============================================================
# RAW DATA QUALITY
# ============================================================

@st.cache_data
def get_raw_quality():

    results = []

    for dataset_name, filename in DATASETS.items():

        try:

            df = load_raw_dataset(filename)

            total_cells = df.shape[0] * df.shape[1]

            missing = int(
                df.isnull().sum().sum()
            )

            duplicates = int(
                df.duplicated().sum()
            )

            completeness = (
                ((total_cells - missing) / total_cells) * 100
                if total_cells > 0
                else 0
            )

            results.append(
                {
                    "Dataset": dataset_name,
                    "Rows": len(df),
                    "Columns": len(df.columns),
                    "Missing Values": missing,
                    "Duplicates": duplicates,
                    "Completeness": round(
                        completeness, 2
                    ),
                }
            )

        except Exception:

            continue

    return pd.DataFrame(results)


# ============================================================
# PROCESSED QUALITY
# ============================================================

@st.cache_data
def get_processed_quality():

    df = load_processed_data()

    total_cells = df.shape[0] * df.shape[1]

    missing = int(
        df.isnull().sum().sum()
    )

    duplicates = int(
        df.duplicated().sum()
    )

    completeness = (
        ((total_cells - missing) / total_cells) * 100
        if total_cells > 0
        else 0
    )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing": missing,
        "duplicates": duplicates,
        "completeness": completeness,
    }


# ============================================================
# PIPELINE QUALITY CHECKS
# ============================================================

@st.cache_data
def get_pipeline_quality():

    df = load_processed_data()

    missing_order_ids = int(
        df["order_id"].isnull().sum()
    )

    invalid_price = int(
        (df["price"] < 0).sum()
    )

    invalid_total = int(
        (df["total_item_value"] < 0).sum()
    )

    duplicate_groups = int(
        df.duplicated().sum()
    )

    return {
        "missing_order_ids": missing_order_ids,
        "invalid_price": invalid_price,
        "invalid_total": invalid_total,
        "duplicate_groups": duplicate_groups,
    }


# ============================================================
# PIPELINE LOG
# ============================================================

def get_pipeline_status():

    if not LOG_PATH.exists():

        return "Not Available"

    try:

        text = LOG_PATH.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        if "COMPLETE PIPELINE EXECUTION SUCCESSFUL" in text:

            return "Successful"

        if "PIPELINE EXECUTION FAILED" in text:

            return "Failed"

        return "Available"

    except Exception:

        return "Not Available"


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero-title">
        E-Commerce DataForge – ETL & Data Quality
    </div>

    <div class="hero-subtitle">
        Olist Brazilian E-Commerce | Enterprise Data Platform
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## ⚙️ DataForge"
)

st.sidebar.markdown(
    """
    **Pipeline**

    CSV → Parquet → Transformation → 
    Data Quality → DuckDB → Analytics
    """
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### Dataset"
)

st.sidebar.info(
    "Brazilian E-Commerce Public Dataset "
    "by Olist"
)

st.sidebar.markdown("---")

pipeline_status = get_pipeline_status()

if pipeline_status == "Successful":

    st.sidebar.markdown(
        '<span class="success-badge">● Pipeline Successful</span>',
        unsafe_allow_html=True
    )

elif pipeline_status == "Failed":

    st.sidebar.markdown(
        '<span class="warning-badge">● Pipeline Failed</span>',
        unsafe_allow_html=True
    )

else:

    st.sidebar.write(
        f"Pipeline status: {pipeline_status}"
    )


# ============================================================
# LOAD EVERYTHING
# ============================================================

try:

    metrics = get_total_metrics()

    monthly_data = get_monthly_revenue()

    category_data = get_top_categories()

    yearly_data = get_yearly_revenue()

    product_data = get_top_products()

    raw_quality = get_raw_quality()

    processed_quality = get_processed_quality()

    pipeline_quality = get_pipeline_quality()

    processed_df = load_processed_data()

except Exception as error:

    st.error(
        f"Dashboard loading error: {error}"
    )

    st.stop()


# ============================================================
# TOP KPI ROW
# ============================================================

raw_total_rows = int(
    raw_quality["Rows"].sum()
)

raw_total_missing = int(
    raw_quality["Missing Values"].sum()
)

raw_total_duplicates = int(
    raw_quality["Duplicates"].sum()
)

processed_rows = processed_quality["rows"]

processed_missing = processed_quality["missing"]

quality_before = (
    raw_quality["Completeness"].mean()
)

quality_after = (
    processed_quality["completeness"]
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Quality before",
        f"{quality_before:.1f}%"
    )


with col2:

    gain = quality_after - quality_before

    st.metric(
        "Quality after",
        f"{quality_after:.1f}%",
        delta=f"{gain:+.1f}"
    )


with col3:

    st.metric(
        "Valid records stored",
        f"{processed_rows:,}"
    )


with col4:

    st.metric(
        "Records flagged",
        f"{pipeline_quality['invalid_price'] + pipeline_quality['invalid_total']:,}"
    )


st.markdown("---")


# ============================================================
# QUALITY BY SOURCE
# ============================================================

st.header(
    "Data quality by source"
)

st.caption(
    "Completeness, missing values and duplicate records "
    "across the raw Olist datasets."
)


quality_display = raw_quality.copy()

quality_display.columns = [
    "Source",
    "Rows",
    "Columns",
    "Missing Values",
    "Duplicates",
    "Completeness (%)",
]


st.dataframe(
    quality_display,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# QUALITY CHARTS
# ============================================================

chart_col1, chart_col2 = st.columns(2)


# ------------------------------------------------------------
# QUALITY BEFORE VS AFTER
# ------------------------------------------------------------

with chart_col1:

    st.subheader(
        "Overall data quality before vs after ETL"
    )

    quality_chart = pd.DataFrame(
        {
            "Stage": [
                "Before ETL",
                "After ETL"
            ],
            "Quality": [
                quality_before,
                quality_after
            ]
        }
    )

    fig_quality = px.bar(
        quality_chart,
        x="Stage",
        y="Quality",
        range_y=[0, 100],
        text="Quality",
        labels={
            "Quality": "Completeness (%)"
        },
    )

    fig_quality.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_quality.update_layout(
        template="plotly_dark",
        paper_bgcolor="#10141c",
        plot_bgcolor="#10141c",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        ),
    )

    st.plotly_chart(
        fig_quality,
        use_container_width=True
    )


# ------------------------------------------------------------
# RAW COMPLETENESS BY DATASET
# ------------------------------------------------------------

with chart_col2:

    st.subheader(
        "Raw data completeness by source"
    )

    fig_source = px.bar(
        raw_quality,
        x="Dataset",
        y="Completeness",
        labels={
            "Completeness": "Completeness (%)",
            "Dataset": "Source"
        },
    )

    fig_source.update_layout(
        template="plotly_dark",
        paper_bgcolor="#10141c",
        plot_bgcolor="#10141c",
        yaxis=dict(
            range=[0, 100]
        ),
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        ),
    )

    st.plotly_chart(
        fig_source,
        use_container_width=True
    )


# ============================================================
# DATA QUALITY CHECK RESULTS
# ============================================================

st.header(
    "Data quality validation"
)

st.caption(
    "Business-rule checks executed on the processed sales table."
)


q1, q2, q3, q4 = st.columns(4)


with q1:

    st.metric(
        "Missing Order IDs",
        f"{pipeline_quality['missing_order_ids']:,}"
    )


with q2:

    st.metric(
        "Invalid Prices",
        f"{pipeline_quality['invalid_price']:,}"
    )


with q3:

    st.metric(
        "Invalid Total Values",
        f"{pipeline_quality['invalid_total']:,}"
    )


with q4:

    st.metric(
        "Duplicate Records",
        f"{pipeline_quality['duplicate_groups']:,}"
    )


st.markdown("---")


# ============================================================
# RAW VS CLEANED DATA
# ============================================================

st.header(
    "Raw vs cleaned e-commerce data"
)


selected_dataset = st.selectbox(
    "Source dataset",
    list(DATASETS.keys())
)


raw_selected = load_raw_dataset(
    DATASETS[selected_dataset]
)


raw_col, clean_col = st.columns(2)


# ------------------------------------------------------------
# RAW DATA
# ------------------------------------------------------------

with raw_col:

    st.subheader(
        "Raw (dirty) records"
    )

    st.caption(
        f"{selected_dataset} — original CSV"
    )

    st.dataframe(
        raw_selected.head(10),
        use_container_width=True,
        height=360,
    )


# ------------------------------------------------------------
# PROCESSED DATA
# ------------------------------------------------------------

with clean_col:

    st.subheader(
        "Clean / processed records"
    )

    st.caption(
        "fact_sales.parquet"
    )

    st.dataframe(
        processed_df.head(10),
        use_container_width=True,
        height=360,
    )


st.markdown("---")


# ============================================================
# TRANSFORMATION SUMMARY
# ============================================================

st.header(
    "Transformation summary"
)


summary_col1, summary_col2 = st.columns(2)


with summary_col1:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-title">
        🔴 Raw data
        </div>

        <div class="info-text">

        • 9 CSV source datasets<br>
        • Separate entities and relationships<br>
        • Raw timestamps<br>
        • Missing values present<br>
        • Different schemas per dataset<br>
        • No unified sales table

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with summary_col2:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-title">
        🟢 Processed data
        </div>

        <div class="info-text">

        • Delivered orders selected<br>
        • Orders joined with order items<br>
        • Products and categories joined<br>
        • Timestamp converted to date fields<br>
        • Total item value calculated<br>
        • Duplicate records removed<br>
        • Stored as Parquet

        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# REVENUE ANALYTICS
# ============================================================

st.header(
    "Business analytics"
)


# ------------------------------------------------------------
# MONTHLY REVENUE
# ------------------------------------------------------------

st.subheader(
    "Monthly revenue trend"
)


fig_monthly = px.line(
    monthly_data,
    x="order_year_month",
    y="revenue",
    markers=True,
    labels={
        "order_year_month": "Month",
        "revenue": "Revenue"
    },
)


fig_monthly.update_layout(
    template="plotly_dark",
    paper_bgcolor="#10141c",
    plot_bgcolor="#10141c",
    hovermode="x unified",
)


st.plotly_chart(
    fig_monthly,
    use_container_width=True
)


# ============================================================
# CATEGORY + YEAR
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Top product categories"
    )

    category_chart = px.bar(
        category_data,
        x="revenue",
        y="category",
        orientation="h",
        labels={
            "revenue": "Revenue",
            "category": "Category"
        },
    )

    category_chart.update_layout(
        template="plotly_dark",
        paper_bgcolor="#10141c",
        plot_bgcolor="#10141c",
        yaxis={
            "categoryorder": "total ascending"
        },
    )

    st.plotly_chart(
        category_chart,
        use_container_width=True
    )


with col2:

    st.subheader(
        "Yearly revenue"
    )

    yearly_chart = px.bar(
        yearly_data,
        x="order_year",
        y="revenue",
        labels={
            "order_year": "Year",
            "revenue": "Revenue"
        },
    )

    yearly_chart.update_layout(
        template="plotly_dark",
        paper_bgcolor="#10141c",
        plot_bgcolor="#10141c",
    )

    st.plotly_chart(
        yearly_chart,
        use_container_width=True
    )


# ============================================================
# TOP PRODUCTS
# ============================================================

st.subheader(
    "Top products by revenue"
)


st.dataframe(
    product_data,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# PIPELINE ARCHITECTURE
# ============================================================

st.markdown("---")

st.header(
    "Pipeline architecture"
)


architecture = """
RAW CSV DATA
     ↓
PANDAS INGESTION
     ↓
RAW PARQUET DATA LAKE
     ↓
DATA TRANSFORMATION
     ↓
PROCESSED fact_sales.parquet
     ↓
DATA QUALITY VALIDATION
     ↓
DUCKDB DATA WAREHOUSE
     ↓
ANALYTICS LAYER
     ↓
PLOTLY + STREAMLIT DASHBOARD
"""


st.code(
    architecture,
    language="text"
)


# ============================================================
# PIPELINE STAGES
# ============================================================

stage_col1, stage_col2, stage_col3, stage_col4 = st.columns(4)


with stage_col1:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-title">
        01 — Ingestion
        </div>

        <div class="info-text">
        CSV files are read using Pandas
        and converted into Parquet files.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with stage_col2:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-title">
        02 — Transformation
        </div>

        <div class="info-text">
        Orders, items, products and
        categories are combined into
        a sales fact table.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with stage_col3:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-title">
        03 — Data Quality
        </div>

        <div class="info-text">
        Missing IDs, invalid values
        and duplicate records are
        validated.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with stage_col4:

    st.markdown(
        """
        <div class="info-card">

        <div class="info-title">
        04 — Warehouse
        </div>

        <div class="info-text">
        Processed Parquet data is
        loaded into DuckDB for
        analytical queries.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "E-Commerce DataForge | "
    "Python • Pandas • Parquet • DuckDB • Plotly • Streamlit"
)