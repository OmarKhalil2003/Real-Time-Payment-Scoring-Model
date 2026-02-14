import streamlit as st
import pandas as pd
import time
import io
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError
from app.config.settings import settings

# -----------------------------------
# Database Connection
# -----------------------------------

DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:"
    f"{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:"
    f"{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

st.set_page_config(page_title="Fraud Monitoring Console", layout="wide")
st.title("🛡 Real-Time Fraud Monitoring Console")

# -----------------------------------
# Sidebar Controls
# -----------------------------------

st.sidebar.header("Controls")

auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)

refresh_interval = st.sidebar.slider(
    "Refresh Interval (seconds)",
    min_value=1,
    max_value=5,
    value=3
)

time_window = st.sidebar.slider(
    "Recent Activity Window (minutes)",
    min_value=1,
    max_value=15,
    value=5
)

customer_filter = st.sidebar.text_input("Customer ID")


# -----------------------------------
# Ensure Table Exists
# -----------------------------------

def table_exists(table_name):
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except OperationalError:
        return False


if not table_exists("scored_transactions"):
    st.warning("Waiting for scoring service to initialize database...")
    st.stop()


# -----------------------------------
# CSV Export Helper
# -----------------------------------

def download_csv(df, filename, label):
    if df.empty:
        st.warning("No data available for export.")
        return
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    st.download_button(
        label=label,
        data=buffer.getvalue(),
        file_name=filename,
        mime="text/csv"
    )


# -----------------------------------
# Queries
# -----------------------------------

def load_lifetime_totals():
    query = """
        SELECT status, COUNT(*) as total
        FROM scored_transactions
        GROUP BY status
    """
    return pd.read_sql(query, engine)


def load_throughput():
    query = """
        SELECT COUNT(*) as tx_last_min
        FROM scored_transactions
        WHERE created_at >= NOW() - INTERVAL 1 MINUTE
    """
    return pd.read_sql(query, engine)


def load_fraud_source_breakdown():
    query = """
        SELECT reason, COUNT(*) as total
        FROM scored_transactions
        GROUP BY reason
    """
    return pd.read_sql(query, engine)


def load_latency_metrics():
    query = """
        SELECT 
            AVG(TIMESTAMPDIFF(MICROSECOND, created_at, processed_at))/1000 as avg_latency_ms,
            MAX(TIMESTAMPDIFF(MICROSECOND, created_at, processed_at))/1000 as max_latency_ms
        FROM scored_transactions
        WHERE processed_at IS NOT NULL
    """
    return pd.read_sql(query, engine)


def load_recent_high_risk(window):
    query = f"""
        SELECT *
        FROM scored_transactions
        WHERE created_at >= NOW() - INTERVAL {window} MINUTE
        AND score >= 0.8
        ORDER BY score DESC
        LIMIT 50
    """
    return pd.read_sql(query, engine)


def load_top_customers():
    query = """
        SELECT customer_id,
               COUNT(*) as total_tx,
               SUM(CASE WHEN status='DECLINED' THEN 1 ELSE 0 END) as fraud_tx
        FROM scored_transactions
        GROUP BY customer_id
        ORDER BY fraud_tx DESC
        LIMIT 10
    """
    return pd.read_sql(query, engine)


def load_velocity_suspects(window):
    query = f"""
        SELECT customer_id, COUNT(*) as tx_count
        FROM scored_transactions
        WHERE created_at >= NOW() - INTERVAL {window} MINUTE
        GROUP BY customer_id
        HAVING tx_count >= 8
        ORDER BY tx_count DESC
    """
    return pd.read_sql(query, engine)


def load_customer_lifetime(customer_id):
    query = text("""
        SELECT 
            COUNT(*) as total_tx,
            SUM(CASE WHEN status = 'DECLINED' THEN 1 ELSE 0 END) as fraud_tx,
            AVG(score) as avg_score
        FROM scored_transactions
        WHERE customer_id = :customer_id
    """)
    return pd.read_sql(query, engine, params={"customer_id": customer_id})


def load_full_dataset(limit=None, status=None):
    base_query = "SELECT * FROM scored_transactions"
    conditions = []

    if status:
        conditions.append(f"status = '{status}'")

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY created_at DESC"

    if limit:
        base_query += f" LIMIT {limit}"

    return pd.read_sql(base_query, engine)


# -----------------------------------
# Load Core Data
# -----------------------------------

totals = load_lifetime_totals()
throughput_df = load_throughput()
fraud_source_df = load_fraud_source_breakdown()
latency_df = load_latency_metrics()

if totals.empty:
    st.warning("No transactions available yet.")
    st.stop()

# -----------------------------------
# SYSTEM HEALTH PANEL
# -----------------------------------

st.subheader("📊 System Health")

col1, col2, col3, col4 = st.columns(4)

declined = int(totals.loc[totals["status"] == "DECLINED", "total"].sum())
review = int(totals.loc[totals["status"] == "REVIEW", "total"].sum())
approved = int(totals.loc[totals["status"] == "APPROVED", "total"].sum())
tpm = int(throughput_df["tx_last_min"].iloc[0])

col1.metric("DECLINED", declined)
col2.metric("REVIEW", review)
col3.metric("APPROVED", approved)
col4.metric("Transactions / Min", tpm)

st.divider()

# -----------------------------------
# EXISTING EXPORT SECTIONS (UNCHANGED)
# -----------------------------------

st.subheader("🧠 Fraud Source Breakdown")
st.dataframe(fraud_source_df, use_container_width=True)
download_csv(fraud_source_df, "fraud_source_breakdown.csv", "⬇ Export Fraud Source Breakdown")

st.subheader("🚨 Top Risk Customers")
top_customers = load_top_customers()
st.dataframe(top_customers, use_container_width=True)
download_csv(top_customers, "top_risk_customers.csv", "⬇ Export Top Risk Customers")

st.subheader("🔥 High Risk Transactions")
high_risk_df = load_recent_high_risk(time_window)
st.dataframe(high_risk_df, use_container_width=True)
download_csv(high_risk_df, "high_risk_transactions.csv", "⬇ Export High Risk Transactions")

st.subheader("⚡ Velocity Alerts")
velocity_df = load_velocity_suspects(time_window)
st.dataframe(velocity_df, use_container_width=True)
download_csv(velocity_df, "velocity_alerts.csv", "⬇ Export Velocity Alerts")

# -----------------------------------
# 🆕 FULL DATASET EXPORT SECTION
# -----------------------------------

st.subheader("📦 Full Dataset Export")

export_limit = st.number_input(
    "Row Limit (0 = export all rows)",
    min_value=0,
    max_value=1000000,
    value=10000,
    step=1000
)

export_status = st.selectbox(
    "Filter by Status",
    ["ALL", "APPROVED", "REVIEW", "DECLINED"]
)

if st.button("Prepare Full Dataset Export"):
    status_filter = None if export_status == "ALL" else export_status
    limit_value = None if export_limit == 0 else export_limit

    full_df = load_full_dataset(limit=limit_value, status=status_filter)

    download_csv(
        full_df,
        "full_scored_transactions.csv",
        "⬇ Download Full Dataset"
    )

# -----------------------------------
# CUSTOMER INVESTIGATION
# -----------------------------------

if customer_filter:
    lifetime_df = load_customer_lifetime(customer_filter)
    if not lifetime_df.empty:
        st.dataframe(lifetime_df)

# -----------------------------------
# Auto Refresh
# -----------------------------------

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
