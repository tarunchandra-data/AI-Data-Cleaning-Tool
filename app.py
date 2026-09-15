import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Data Cleaning Tool",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.dashboard-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.dashboard-subtitle {
    font-size: 17px;
    color: #6b7280;
    margin-bottom: 25px;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    text-align: center;
}

.metric-icon {
    font-size: 28px;
}

.metric-title {
    color: #6b7280;
    font-size: 14px;
    margin-top: 6px;
}
.metric-value {
    font-size: 28px;
    font-weight: 800;
    margin-top: 4px;
    color: #111827 !important;
}

.metric-title {
    color: #6b7280 !important;
    font-size: 14px;
    margin-top: 6px;
}


.section-title {
    font-size: 25px;
    font-weight: 750;
    margin-top: 35px;
    margin-bottom: 15px;
}

.info-box {
    padding: 18px;
    border-radius: 12px;
    background: white;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.footer {
    text-align: center;
    color: #6b7280;
    margin-top: 50px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🧹 AI Data Cleaner")

    st.markdown(
        "Clean, analyze and visualize your datasets with ease."
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "📂 Upload Dataset",
        type=["csv", "xlsx"],
        help="Upload CSV or Excel file"
    )

    st.divider()

    st.markdown("### ⚙️ Settings")

    show_preview = st.checkbox(
        "Show Dataset Preview",
        value=True
    )

    st.markdown("---")

    st.caption("AI-Powered Data Cleaning & Analysis Tool")
    st.caption("Built with Python • Pandas • Plotly • Streamlit")


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">🧹 AI-Powered Data Cleaning & Analysis Tool</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Upload your dataset and automatically clean, analyze and visualize your data.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# NO FILE UPLOADED
# ============================================================

if uploaded_file is None:

    st.info(
        "👈 Please upload a CSV or Excel file from the sidebar to get started."
    )

    st.markdown("### 🚀 What this tool can do")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="info-box">
            <h3>🧹 Data Cleaning</h3>
            <p>Handle missing values, duplicates and unwanted columns.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="info-box">
            <h3>📊 Data Analysis</h3>
            <p>Explore statistics, correlations, distributions and outliers.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="info-box">
            <h3>📈 Visualization</h3>
            <p>Create interactive and professional charts from your data.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

try:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(f"❌ Could not read the file: {e}")
    st.stop()


if df.empty:

    st.warning("The uploaded dataset is empty.")
    st.stop()


original_df = df.copy()


# ============================================================
# DATA QUALITY SCORE
# ============================================================

rows = len(df)
columns = len(df.columns)

missing_count = int(df.isnull().sum().sum())
duplicate_count = int(df.duplicated().sum())

total_cells = rows * columns

if total_cells > 0:
    missing_percentage = (missing_count / total_cells) * 100
else:
    missing_percentage = 0

duplicate_percentage = (
    (duplicate_count / rows) * 100
    if rows > 0 else 0
)

quality_score = max(
    0,
    round(
        100
        - (missing_percentage * 0.6)
        - (duplicate_percentage * 0.4),
        1
    )
)


# ============================================================
# DASHBOARD METRICS
# ============================================================

st.markdown("### 📊 Dataset Overview")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">📄</div>
            <div class="metric-title">Rows</div>
            <div class="metric-value">{rows:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">📋</div>
            <div class="metric-title">Columns</div>
            <div class="metric-value">{columns:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">⚠️</div>
            <div class="metric-title">Missing Values</div>
            <div class="metric-value">{missing_count:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🔁</div>
            <div class="metric-title">Duplicates</div>
            <div class="metric-value">{duplicate_count:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">💯</div>
            <div class="metric-title">Quality Score</div>
            <div class="metric-value">{quality_score}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DATA PREVIEW
# ============================================================

if show_preview:

    st.markdown(
        '<div class="section-title">👀 Dataset Preview</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        df.head(10),
        width="stretch"
    )


# ============================================================
# MISSING VALUES ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🧩 Missing Values Analysis</div>',
    unsafe_allow_html=True
)

missing_table = pd.DataFrame({
    "Column": df.columns,
    "Missing Values": df.isnull().sum().values,
    "Missing %": (
        df.isnull().sum().values / len(df) * 100
    ).round(2)
})

missing_table = missing_table[
    missing_table["Missing Values"] > 0
]

if missing_table.empty:

    st.success("✅ No missing values found.")

else:

    st.dataframe(
        missing_table,
        width="stretch"
    )

    cleaning_method = st.selectbox(
        "Choose method for missing values",
        [
            "Do Nothing",
            "Fill Numeric with Median",
            "Fill Numeric with Mean",
            "Fill All with 0",
            "Drop Rows with Missing Values"
        ]
    )

    if cleaning_method == "Fill Numeric with Median":

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns

        for col in numeric_columns:
            df[col] = df[col].fillna(df[col].median())

        st.success("✅ Missing numeric values filled using median.")

    elif cleaning_method == "Fill Numeric with Mean":

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns

        for col in numeric_columns:
            df[col] = df[col].fillna(df[col].mean())

        st.success("✅ Missing numeric values filled using mean.")

    elif cleaning_method == "Fill All with 0":

        df = df.fillna(0)

        st.success("✅ Missing values filled with 0.")

    elif cleaning_method == "Drop Rows with Missing Values":

        before = len(df)

        df = df.dropna()

        removed = before - len(df)

        st.success(
            f"✅ Removed {removed} rows containing missing values."
        )


# ============================================================
# DUPLICATE HANDLING
# ============================================================

st.markdown(
    '<div class="section-title">🔁 Duplicate Handling</div>',
    unsafe_allow_html=True
)

current_duplicates = int(df.duplicated().sum())

st.write(
    f"Current duplicate rows: **{current_duplicates}**"
)

if current_duplicates > 0:

    remove_duplicates = st.checkbox(
        "Remove duplicate rows"
    )

    if remove_duplicates:

        before = len(df)

        df = df.drop_duplicates()

        removed = before - len(df)

        st.success(
            f"✅ Removed {removed} duplicate rows."
        )

else:

    st.success("✅ No duplicate rows found.")


# ============================================================
# COLUMN REMOVAL
# ============================================================

st.markdown(
    '<div class="section-title">🗑️ Remove Unwanted Columns</div>',
    unsafe_allow_html=True
)

columns_to_remove = st.multiselect(
    "Select columns you want to remove",
    df.columns.tolist()
)

if columns_to_remove:

    df = df.drop(
        columns=columns_to_remove
    )

    st.success(
        f"✅ Removed {len(columns_to_remove)} column(s)."
    )


# ============================================================
# CLEANED DATASET
# ============================================================

st.markdown(
    '<div class="section-title">✨ Cleaned Dataset</div>',
    unsafe_allow_html=True
)

st.dataframe(
    df.head(20),
    width="stretch"
)


# ============================================================
# BEFORE VS AFTER
# ============================================================

st.markdown(
    '<div class="section-title">📋 Before vs After Cleaning</div>',
    unsafe_allow_html=True
)

before_rows = len(original_df)
after_rows = len(df)

before_missing = int(
    original_df.isnull().sum().sum()
)

after_missing = int(
    df.isnull().sum().sum()
)

before_duplicates = int(
    original_df.duplicated().sum()
)

after_duplicates = int(
    df.duplicated().sum()
)

comparison = pd.DataFrame({
    "Metric": [
        "Rows",
        "Missing Values",
        "Duplicate Rows"
    ],
    "Before Cleaning": [
        before_rows,
        before_missing,
        before_duplicates
    ],
    "After Cleaning": [
        after_rows,
        after_missing,
        after_duplicates
    ]
})

st.dataframe(
    comparison,
    width="stretch"
)


# ============================================================
# CLEANING SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">📝 Cleaning Summary</div>',
    unsafe_allow_html=True
)

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.metric(
        "Rows Removed",
        before_rows - after_rows
    )

with summary_col2:
    st.metric(
        "Missing Values Removed",
        before_missing - after_missing
    )

with summary_col3:
    st.metric(
        "Duplicates Removed",
        before_duplicates - after_duplicates
    )


# ============================================================
# STATISTICAL ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Statistical Analysis</div>',
    unsafe_allow_html=True
)

numeric_df = df.select_dtypes(
    include=np.number
)

if not numeric_df.empty:

    st.dataframe(
        numeric_df.describe().round(2),
        width="stretch"
    )

else:

    st.info("No numeric columns available for statistical analysis.")


# ============================================================
# PROFESSIONAL VISUALIZATIONS
# ============================================================

st.markdown(
    '<div class="section-title">📈 Professional Data Visualization</div>',
    unsafe_allow_html=True
)

numeric_columns = df.select_dtypes(
    include=np.number
).columns.tolist()

categorical_columns = df.select_dtypes(
    exclude=np.number
).columns.tolist()


# ------------------------------------------------------------
# HISTOGRAM
# ------------------------------------------------------------

if numeric_columns:

    selected_hist = st.selectbox(
        "📊 Histogram - Select numeric column",
        numeric_columns,
        key="histogram_column"
    )

    fig_hist = px.histogram(
        df,
        x=selected_hist,
        nbins=20,
        marginal="box",
        title=f"Distribution of {selected_hist}"
    )

    fig_hist.update_layout(
        height=500,
        template="plotly_white"
    )

    st.plotly_chart(
        fig_hist,
        width="stretch"
    )


# ------------------------------------------------------------
# BOX PLOT
# ------------------------------------------------------------

if numeric_columns:

    selected_box = st.selectbox(
        "📦 Box Plot - Select numeric column",
        numeric_columns,
        key="box_column"
    )

    fig_box = px.box(
        df,
        y=selected_box,
        points="outliers",
        title=f"Box Plot of {selected_box}"
    )

    fig_box.update_layout(
        height=500,
        template="plotly_white"
    )

    st.plotly_chart(
        fig_box,
        width="stretch"
    )


# ------------------------------------------------------------
# CORRELATION HEATMAP
# ------------------------------------------------------------

if len(numeric_columns) >= 2:

    correlation = df[numeric_columns].corr()

    fig_corr = px.imshow(
        correlation,
        text_auto=True,
        aspect="auto",
        title="🔥 Correlation Heatmap"
    )

    fig_corr.update_layout(
        height=550
    )

    st.plotly_chart(
        fig_corr,
        width="stretch"
    )


# ------------------------------------------------------------
# SCATTER PLOT
# ------------------------------------------------------------

if len(numeric_columns) >= 2:

    scatter_col1, scatter_col2 = st.columns(2)

    with scatter_col1:

        x_column = st.selectbox(
            "🔵 X-axis",
            numeric_columns,
            key="scatter_x"
        )

    with scatter_col2:

        y_options = [
            col for col in numeric_columns
            if col != x_column
        ]

        y_column = st.selectbox(
            "🔵 Y-axis",
            y_options,
            key="scatter_y"
        )

    fig_scatter = px.scatter(
        df,
        x=x_column,
        y=y_column,
        title=f"{x_column} vs {y_column}",
        trendline="ols"
    )

    fig_scatter.update_layout(
        height=550,
        template="plotly_white"
    )

    st.plotly_chart(
        fig_scatter,
        width="stretch"
    )


# ------------------------------------------------------------
# CATEGORICAL BAR CHART
# ------------------------------------------------------------

if categorical_columns:

    selected_cat = st.selectbox(
        "📊 Category Column",
        categorical_columns,
        key="category_column"
    )

    category_counts = (
        df[selected_cat]
        .value_counts()
        .head(15)
        .reset_index()
    )

    category_counts.columns = [
        selected_cat,
        "Count"
    ]

    fig_bar = px.bar(
        category_counts,
        x=selected_cat,
        y="Count",
        title=f"Top Categories - {selected_cat}"
    )

    fig_bar.update_layout(
        height=500,
        template="plotly_white"
    )

    st.plotly_chart(
        fig_bar,
        width="stretch"
    )


# ------------------------------------------------------------
# LINE CHART
# ------------------------------------------------------------

if numeric_columns:

    selected_line = st.selectbox(
        "📈 Line Chart Column",
        numeric_columns,
        key="line_column"
    )

    fig_line = px.line(
        df.reset_index(),
        x="index",
        y=selected_line,
        title=f"{selected_line} Trend"
    )

    fig_line.update_layout(
        height=500,
        template="plotly_white",
        xaxis_title="Row Index",
        yaxis_title=selected_line
    )

    st.plotly_chart(
        fig_line,
        width="stretch"
    )


# ============================================================
# OUTLIER DETECTION
# ============================================================

st.markdown(
    '<div class="section-title">🚨 Outlier Detection</div>',
    unsafe_allow_html=True
)

if numeric_columns:

    outlier_results = []

    for col in numeric_columns:

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)

        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[
            (df[col] < lower) |
            (df[col] > upper)
        ]

        outlier_results.append({
            "Column": col,
            "Outliers": len(outliers),
            "Lower Bound": round(lower, 2),
            "Upper Bound": round(upper, 2)
        })

    outlier_df = pd.DataFrame(
        outlier_results
    )

    st.dataframe(
        outlier_df,
        width="stretch"
    )

else:

    st.info(
        "No numeric columns available for outlier detection."
    )


# ============================================================
# AI DATA SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">🤖 AI Data Summary</div>',
    unsafe_allow_html=True
)

summary_text = f"""
### Dataset Overview

- **Total Rows:** {len(df):,}
- **Total Columns:** {len(df.columns):,}
- **Missing Values:** {int(df.isnull().sum().sum()):,}
- **Duplicate Rows:** {int(df.duplicated().sum()):,}
- **Numeric Columns:** {len(numeric_columns)}
- **Categorical Columns:** {len(categorical_columns)}

The dataset has been analyzed for missing values, duplicates,
statistical patterns and potential outliers.
"""

st.markdown(summary_text)


# ============================================================
# AI CLEANING RECOMMENDATIONS
# ============================================================

st.markdown(
    '<div class="section-title">💡 AI Cleaning Recommendations</div>',
    unsafe_allow_html=True
)

recommendations = []

current_missing = int(
    df.isnull().sum().sum()
)

current_duplicates = int(
    df.duplicated().sum()
)

if current_missing > 0:

    recommendations.append(
        "⚠️ Missing values are present. Consider filling numeric values using median or mean."
    )

else:

    recommendations.append(
        "✅ No missing values detected."
    )


if current_duplicates > 0:

    recommendations.append(
        "⚠️ Duplicate rows are present. Consider removing duplicate records."
    )

else:

    recommendations.append(
        "✅ No duplicate rows detected."
    )


if numeric_columns:

    recommendations.append(
        "📊 Numeric columns are available for statistical analysis and visualization."
    )


if len(numeric_columns) >= 2:

    recommendations.append(
        "🔥 Multiple numeric columns detected. Check the correlation heatmap for relationships."
    )


for recommendation in recommendations:

    st.write(recommendation)


# ============================================================
# DATA QUALITY REPORT
# ============================================================

st.markdown(
    '<div class="section-title">📋 Data Quality Report</div>',
    unsafe_allow_html=True
)

final_missing = int(
    df.isnull().sum().sum()
)

final_duplicates = int(
    df.duplicated().sum()
)

final_cells = len(df) * len(df.columns)

if final_cells > 0:

    final_missing_percentage = (
        final_missing / final_cells
    ) * 100

else:

    final_missing_percentage = 0


final_quality_score = max(
    0,
    round(
        100 - final_missing_percentage * 0.6,
        1
    )
)


quality_col1, quality_col2, quality_col3 = st.columns(3)

with quality_col1:

    st.metric(
        "Final Quality Score",
        f"{final_quality_score}%"
    )

with quality_col2:

    st.metric(
        "Final Missing Values",
        final_missing
    )

with quality_col3:

    st.metric(
        "Final Duplicates",
        final_duplicates
    )


# ============================================================
# DOWNLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📥 Download Cleaned Dataset</div>',
    unsafe_allow_html=True
)


# CSV

csv_data = df.to_csv(
    index=False
).encode("utf-8")


# Excel

excel_buffer = io.BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        index=False,
        sheet_name="Cleaned Data"
    )

excel_data = excel_buffer.getvalue()


download_col1, download_col2 = st.columns(2)

with download_col1:

    st.download_button(
        label="⬇️ Download Cleaned CSV",
        data=csv_data,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        width="stretch"
    )

with download_col2:

    st.download_button(
        label="⬇️ Download Cleaned Excel",
        data=excel_data,
        file_name="cleaned_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🧹 <b>AI-Powered Data Cleaning & Analysis Tool</b><br>
        Built with Python • Pandas • NumPy • Plotly • Streamlit
    </div>
    """,
    unsafe_allow_html=True
)