
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Customer & Car Analytics",
    page_icon="🚗",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv("cleaned_cars_data.csv")
    return data

df = load_data()

# Exclude identifier and postal code from analysis displays
df = df.drop(columns=["INDEX", "POSTAL CODE"], errors="ignore")

# ---------------- TITLE ----------------
st.title("🚗 Customer & Car Analytics Dashboard")
st.markdown(
    "Explore customer demographics, income, car ownership "
    "and driving behaviour."
)

st.divider()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Dashboard Filters")

filtered_df = df.copy()

filter_columns = [
    "CITY",
    "CAR TYPE",
    "JOB",
    "EDUCATION",
    "SEX",
    "MARITAL STATUS",
    "USE"
]

for column in filter_columns:
    if column in filtered_df.columns:
        options = sorted(
            filtered_df[column].dropna().unique().tolist()
        )

        selected = st.sidebar.multiselect(
            f"Filter by {column.title()}",
            options,
            default=options
        )

        filtered_df = filtered_df[
            filtered_df[column].isin(selected)
        ]

# ---------------- KPI METRICS ----------------
st.subheader("📊 Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Customers", f"{len(filtered_df):,}")

if "INCOME" in filtered_df.columns:
    c2.metric(
        "Average Income",
        f"${filtered_df['INCOME'].mean():,.0f}"
        if not filtered_df.empty else "N/A"
    )

if "CAR AGE" in filtered_df.columns:
    c3.metric(
        "Average Car Age",
        f"{filtered_df['CAR AGE'].mean():.1f} years"
        if not filtered_df.empty else "N/A"
    )

if "MILES CLOCKED" in filtered_df.columns:
    c4.metric(
        "Average Miles Clocked",
        f"{filtered_df['MILES CLOCKED'].mean():,.0f}"
        if not filtered_df.empty else "N/A"
    )

st.divider()

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------------- CUSTOMER DEMOGRAPHICS ----------------
st.subheader("👥 Customer Demographics")

col1, col2 = st.columns(2)

with col1:
    fig = px.pie(
        filtered_df,
        names="SEX",
        title="Customer Distribution by Sex",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        filtered_df["EDUCATION"].value_counts().reset_index(),
        x="EDUCATION",
        y="count",
        title="Customers by Education Level",
        labels={"count": "Number of Customers"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CAR ANALYSIS ----------------
st.subheader("🚘 Car Ownership Analysis")

col1, col2 = st.columns(2)

with col1:
    car_counts = (
        filtered_df["CAR TYPE"]
        .value_counts()
        .reset_index()
    )

    fig = px.bar(
        car_counts,
        x="CAR TYPE",
        y="count",
        title="Customer Distribution by Car Type",
        labels={"count": "Number of Customers"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(
        filtered_df,
        x="CAR TYPE",
        y="CAR AGE",
        color="CAR TYPE",
        title="Car Age Distribution by Car Type"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- INCOME ANALYSIS ----------------
st.subheader("💰 Income Analysis")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        filtered_df,
        x="INCOME",
        nbins=20,
        title="Customer Income Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    income_by_job = (
        filtered_df.groupby("JOB", as_index=False)["INCOME"]
        .mean()
        .sort_values("INCOME", ascending=False)
    )

    fig = px.bar(
        income_by_job,
        x="JOB",
        y="INCOME",
        title="Average Income by Job",
        labels={"INCOME": "Average Income"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- DRIVING BEHAVIOUR ----------------
st.subheader("🛣️ Driving Behaviour")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        filtered_df,
        x="MILES CLOCKED",
        nbins=20,
        title="Distribution of Miles Clocked"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter(
        filtered_df,
        x="TRAVEL TIME",
        y="MILES CLOCKED",
        color="CAR TYPE",
        hover_data=["JOB", "INCOME"],
        title="Travel Time vs Miles Clocked"
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------- BUSINESS INSIGHTS ----------------
st.divider()
st.subheader("💡 Key Business Insights")

col1, col2 = st.columns(2)

with col1:
    most_common_car = filtered_df["CAR TYPE"].mode()[0]
    most_common_use = filtered_df["USE"].mode()[0]

    st.info(
        f"🚗 **Most Popular Car Type:** {most_common_car}"
    )

    st.info(
        f"🛣️ **Most Common Vehicle Usage:** {most_common_use}"
    )

with col2:
    highest_income_job = (
        filtered_df.groupby("JOB")["INCOME"]
        .mean()
        .idxmax()
    )

    highest_job_income = (
        filtered_df.groupby("JOB")["INCOME"]
        .mean()
        .max()
    )

    st.success(
        f"💼 **Highest Average Income Job:** "
        f"{highest_income_job} (${highest_job_income:,.0f})"
    )

    st.info(
        f"📊 **Average Customer Income:** "
        f"${filtered_df['INCOME'].mean():,.0f}"
    )

st.caption(
    "Insights are calculated dynamically based on the selected filters."
)

# ---------------- DOWNLOAD ----------------
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_car_customer_data.csv",
    mime="text/csv"
)

# ---------------- STATISTICAL SUMMARY ----------------
with st.expander("View Statistical Summary"):
    st.write(filtered_df.describe())

st.caption(
    "Car EDA Project | Built using Python, Pandas, "
    "Streamlit and Plotly"
)
