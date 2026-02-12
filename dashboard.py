import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from app.config.settings import settings
import time

# -----------------------------------
# Database Connection
# -----------------------------------

DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:"
    f"{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:"
    f"{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
)

engine = create_engine(DATABASE_URL)

st.set_page_config(page_title="Real-Time Fraud Dashboard", layout="wide")
st.title("💳 Real-Time Payment Scoring Dashboard")

# -----------------------------------
# Sidebar Controls
# -----------------------------------

st.sidebar.header("Controls")

auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 2, 15, 5)

customer_filter = st.sidebar.text_input("Customer ID (optional)")

# -----------------------------------
# Data Loader
# -----------------------------------

@st.cache_data(ttl=5)
def load_data():
    query = "SELECT * FROM scored_transactions ORDER BY created_at DESC LIMIT 1000"
    df = pd.read_sql(query, engine)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df

df = load_data()

if df.empty:
    st.warning("No transactions available yet.")
    st.stop()

# -----------------------------------
# Apply Customer Filter
# -----------------------------------

if customer_filter:
    df = df[df["customer_id"] == customer_filter]

# -----------------------------------
# Metrics Section
# -----------------------------------

col1, col2, col3 = st.columns(3)

declined = df[df["status"] == "DECLINED"].shape[0]
review = df[df["status"] == "REVIEW"].shape[0]
approved = df[df["status"] == "APPROVED"].shape[0]

col1.metric("DECLINED", declined)
col2.metric("REVIEW", review)
col3.metric("APPROVED", approved)

fraud_rate = (declined / len(df)) * 100 if len(df) > 0 else 0
st.metric("Fraud Rate (%)", f"{fraud_rate:.2f}%")

st.divider()

# -----------------------------------
# 📈 Fraud Over Time Chart
# -----------------------------------

st.subheader("📈 Fraud Over Time")

df_time = df.copy()
df_time["minute"] = df_time["created_at"].dt.floor("T")

fraud_over_time = (
    df_time[df_time["status"] == "DECLINED"]
    .groupby("minute")
    .size()
    .reset_index(name="fraud_count")
)

st.line_chart(fraud_over_time.set_index("minute"))

st.divider()

# -----------------------------------
# 👤 Customer Risk Profile
# -----------------------------------

st.subheader("👤 Customer Risk Profile")

if customer_filter:
    total_tx = df.shape[0]
    fraud_tx = df[df["status"] == "DECLINED"].shape[0]
    avg_score = df["score"].mean()

    st.write(f"Total Transactions: {total_tx}")
    st.write(f"Fraud Transactions: {fraud_tx}")
    st.write(f"Average Risk Score: {avg_score:.4f}")

    st.dataframe(df.sort_values("created_at", ascending=False).head(20),
                 use_container_width=True)
else:
    st.info("Enter a Customer ID in sidebar to view profile.")

st.divider()

# -----------------------------------
# Latest Transactions
# -----------------------------------

st.subheader("Latest Transactions")
st.dataframe(df.sort_values("created_at", ascending=False).head(50),
             use_container_width=True)

# -----------------------------------
# 🔄 Auto Refresh
# -----------------------------------

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
