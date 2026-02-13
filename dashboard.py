import streamlit as st
import pandas as pd
import time
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

st.set_page_config(page_title="Real-Time Fraud Dashboard", layout="wide")
st.title("💳 Real-Time Payment Scoring Dashboard")

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
customer_filter = st.sidebar.text_input("Customer ID (optional)")

# -----------------------------------
# Safety: Wait Until Table Exists
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
# Data Loaders
# -----------------------------------

def load_recent_data():
    query = """
        SELECT *
        FROM scored_transactions
        ORDER BY created_at DESC
        LIMIT 500
    """
    df = pd.read_sql(query, engine)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df


@st.cache_data(ttl=10)
def load_lifetime_totals():
    query = """
        SELECT status, COUNT(*) as total
        FROM scored_transactions
        GROUP BY status
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

    return pd.read_sql(
        query,
        engine,
        params={"customer_id": customer_id}
    )

# -----------------------------------
# Load Data
# -----------------------------------

df = load_recent_data()
totals = load_lifetime_totals()

if totals.empty:
    st.warning("No transactions available yet.")
    st.stop()

# -----------------------------------
# Lifetime Metrics
# -----------------------------------

col1, col2, col3 = st.columns(3)

declined = int(totals.loc[totals["status"] == "DECLINED", "total"].sum())
review = int(totals.loc[totals["status"] == "REVIEW", "total"].sum())
approved = int(totals.loc[totals["status"] == "APPROVED", "total"].sum())

col1.metric("DECLINED", declined)
col2.metric("REVIEW", review)
col3.metric("APPROVED", approved)

total_all = declined + review + approved
fraud_rate = (declined / total_all) * 100 if total_all > 0 else 0

st.metric("Fraud Rate (%) - Lifetime", f"{fraud_rate:.2f}%")

st.divider()

# -----------------------------------
# Fraud Over Time
# -----------------------------------

st.subheader("📈 Fraud Over Time (Last 500 Transactions)")

if not df.empty:
    df_time = df.copy()
    df_time["minute"] = df_time["created_at"].dt.floor("min")

    fraud_over_time = (
        df_time[df_time["status"] == "DECLINED"]
        .groupby("minute")
        .size()
        .reset_index(name="fraud_count")
    )

    if not fraud_over_time.empty:
        st.line_chart(fraud_over_time.set_index("minute"))
    else:
        st.info("No fraud activity in recent window.")
else:
    st.info("Waiting for transactions...")

st.divider()

# -----------------------------------
# Customer Risk Profile
# -----------------------------------

st.subheader("👤 Customer Risk Profile")

if customer_filter:
    lifetime_df = load_customer_lifetime(customer_filter)

    if not lifetime_df.empty and lifetime_df["total_tx"].iloc[0] > 0:

        total_tx = int(lifetime_df["total_tx"].iloc[0])
        fraud_tx = int(lifetime_df["fraud_tx"].iloc[0] or 0)
        avg_score = float(lifetime_df["avg_score"].iloc[0] or 0)

        st.write(f"Lifetime Transactions: {total_tx}")
        st.write(f"Lifetime Fraud Transactions: {fraud_tx}")
        st.write(f"Lifetime Average Risk Score: {avg_score:.4f}")

        # Show recent transactions separately
        recent_customer_df = df[df["customer_id"] == customer_filter]

        st.dataframe(
            recent_customer_df.sort_values("created_at", ascending=False).head(20),
            use_container_width=True
        )

    else:
        st.warning("No transactions found for this customer.")
else:
    st.info("Enter a Customer ID in sidebar to view profile.")

st.divider()

# -----------------------------------
# Latest Transactions
# -----------------------------------

st.subheader("Latest Transactions (Last 500)")

if not df.empty:
    st.dataframe(
        df.sort_values("created_at", ascending=False).head(50),
        use_container_width=True
    )
else:
    st.info("No transactions yet.")

# -----------------------------------
# Auto Refresh
# -----------------------------------

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
