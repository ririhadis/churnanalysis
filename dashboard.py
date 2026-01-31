import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from google.cloud import storage
from google.oauth2 import service_account

sns.set(style="darkgrid")

#Konfigurasi
bucket_name = "churn_analy"
blob_path = "dashboard.csv"
local_file = "dashboard.csv"

st.set_page_config(page_title = "Churn Dashboard", layout="wide")

#GCP Client
@st.cache_resource
def create_gcp_client():
    if "gcp_service_account" in st.secrets:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        project_id = st.secrets["gcp_service_account"]["project_id"]
        return storage.Client(credentials=credentials, project=project_id)

#Load data from gcp
@st.cache_data
def load_data_from_gcp():
    client = create_gcp_client()
    
    try:
        if not os.path.exists(local_file):
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            blob.download_to_filename(local_file)
            
        df = pd.read_csv(local_file, parse_dates=["last_trx_date"])
        df["risk_level"] = df["churn_risk"].astype(str)
        
        return df

    except Exception as e:
        st.error("Gagal Load Data dari GCP")
        st.exception(e)
        st.stop()

df = load_data_from_gcp()

#KPI functions
def compute_kpi(data):
    total_cust = data["customer_id"].nunique()

    if total_cust == 0:
        return 0, 0, 0.0, 0.0, 0.0, 0.0
        
    churned_cust = data[data["churn"] == 1]["customer_id"].nunique()
    churn_rate = churned_cust / total_cust * 100
    retention_rate = 100 - churn_rate

    avg_frequency = data["frequency"].mean()
    avg_monetary = data["monetary"].mean()
    
    return total_cust, churned_cust, churn_rate, retention_rate, avg_frequency, avg_monetary

#Aggregation
def monthly_churn_trend(data):
    monthly= (
        data.groupby(pd.Grouper(key="last_trx_date", freq="M")).agg(
            ttl_cust =("customer_id", "nunique"),
            churn_cust = ("churn", "sum")
        ).reset_index()
    )
    monthly["churn_rate"] = monthly["churn_cust"]/monthly["ttl_cust"]
    return monthly

def churn_by_segment(data, col):
    seg= (
        data.groupby(col).agg(
            total =("customer_id", "nunique"),
            churned =("churn", "sum")
        ).reset_index()
    )
    seg["churn_rate"]= seg["churned"] / seg["total"]
    return seg

#Sidebar filter
st.sidebar.header("🔎 Data Filter")

filtered_df = df.copy()

min_date = df["last_trx_date"].min()
max_date = df["last_trx_date"].max()

start_date, end_date = st.sidebar.date_input(
    "Transaction Date Range",
    value =[min_date, max_date]
)

filtered_df = filtered_df[
    (filtered_df["last_trx_date"] >= pd.to_datetime(start_date)) &
    (filtered_df["last_trx_date"] <= pd.to_datetime(end_date))
    ]

if filtered_df.empty:
    st.warning("Data is empty on date range.")
    st.stop()

trx_filter = st.sidebar.multiselect(
    "Transaction Code",
    sorted(df["trx_code"].unique()),
    default =sorted(df["trx_code"].unique())
)

filtered_df = filtered_df[filtered_df["trx_code"].isin(trx_filter)]

risk_filter = st.sidebar.multiselect(
    "Risk Level",
    sorted(df["risk_level"].unique()),
    default = sorted(df["risk_level"].unique())
)

filtered_df = filtered_df[filtered_df["risk_level"].isin(risk_filter)]

#Dashboard Title
st.title("📉 Customer Churn Analysis Dashboard (Risk-Based)")

#KPI Section
total_cust, churned_cust, churn_rate, retention_rate, avg_frequency, avg_monetary = compute_kpi(filtered_df)

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Total Customers", f"{total_cust:,}")
c2.metric("Churned Customers", f"{churned_cust:,}")
c3.metric("Churn Rate", f"{churn_rate:.2f}%")
c4.metric("Retention Rate", f"{retention_rate:.2f}%")
c5.metric("Avg Frequency", f"{avg_frequency:.2f}")
c6.metric("Avg Monetary", f"{avg_monetary:,.0f}")

st.divider()

#Churn Trend
st.subheader("Churn Segmentation")

for col in ["trx_code", "risk_level"]:
    seg_df = churn_by_segment(filtered_df, col)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data = seg_df, x= col, y="churn_rate", ax=ax)
    ax.set_title(f"Churn Rate by {col}")
    ax.set_ylabel("Churn Rate")
    ax.set_xlabel(col)
    #plt.xticks(rotation=30)
    st.pyplot(fig)

st.divider()

#Distribution
st.subheader("RFM Distribution")

for col in ["frequency", "monetary", "recency_days"]:
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(filtered_df[col], bins =30, kde= True, ax=ax)
    ax.set_title(f"Distribution of {col}")
    st.pyplot(fig)

st.divider()

#Correlation
st.subheader("📈 Correlation Heatmap")

num_cols =[
    "n_trx_code", "monetary", "frequency", "recency_days", "monetary_log", "frequency_log", "recency_days_scale", "churn"]

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(filtered_df[num_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

st.divider()

#Risk Table
st.subheader("🎯 Customer Risk Table")

risk_table = filtered_df[
    ["customer_id", "risk_level", "churn", "frequency", "monetary", "recency_days", "trx_code"]
    ].sort_values(by="recency_days", ascending=False)

st.dataframe(risk_table.head(50), use_container_width=True)

st.divider()

#Customer explorer
st.subheader("🔍 Customer Risk Explorer")

selected_id = st.selectbox(
    "Select Customer ID",
    filtered_df["customer_id"].unique())

cust_row = filtered_df[filtered_df["customer_id"] == selected_id]
st.dataframe(cust_row.T, use_container_width=True)

st.divider()

#Top High Risk
st.subheader("🔥 Top High Risk Customers")

top_risk = (
    filtered_df.assign(
        risk_level_clean = filtered_df["risk_level"].fillna("").str.lower()).query(
        "risk_level_clean.str.contains('high')", engine="python").sort_values(
        by="recency_days", ascending=False).head(10)
)

if top_risk.empty:
    st.info("There is no customer with High Risk level in filter")
else:
    st.dataframe(
        top_risk[[
            "customer_id",
            "recency_days",
            "frequency",
            "risk_level",
            "trx_code"
        ]],

        use_container_width=True
    )
st.dataframe(
    top_risk[["customer_id", "recency_days", "frequency", "risk_level", "trx_code"]],
    use_container_width = True)

st.caption("Risk-based Churn Dashboard | Data source: dashboard.csv (Google Cloud Storage)")
