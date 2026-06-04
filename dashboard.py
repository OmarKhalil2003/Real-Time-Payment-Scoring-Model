import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import io
import json
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

st.set_page_config(
    page_title="Fraud Monitoring Console — MCP Enhanced",
    page_icon="🛡",
    layout="wide",
)

# -----------------------------------
# Custom Styling
# -----------------------------------

st.markdown("""
<style>
    /* Dark-themed metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="stMetric"] label {
        color: #a8b2d1 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ccd6f6 !important;
        font-size: 1.8rem !important;
    }

    /* Section headers */
    .stSubheader {
        border-bottom: 2px solid #0f3460;
        padding-bottom: 8px;
    }

    /* MCP explanation cards */
    .mcp-explanation {
        background: linear-gradient(135deg, #1a1a2e 0%, #0d1b2a 100%);
        border-left: 4px solid #e63946;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        font-size: 0.95rem;
        color: #ccd6f6;
    }
    .mcp-explanation-safe {
        background: linear-gradient(135deg, #1a2e1a 0%, #0d2a1b 100%);
        border-left: 4px solid #2ec4b6;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        font-size: 0.95rem;
        color: #ccd6f6;
    }

    /* Rule tag badges */
    .rule-tag {
        display: inline-block;
        background: #e63946;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px 3px;
    }
    .rule-tag-low {
        background: #2ec4b6;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
    }
</style>
""", unsafe_allow_html=True)


st.title("🛡 Real-Time Fraud Monitoring Console")
st.caption("Kafka + MCP Enhanced Fraud Detection Pipeline")

# -----------------------------------
# Sidebar Controls
# -----------------------------------

st.sidebar.header("⚙️ Controls")

auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)

refresh_interval = st.sidebar.slider(
    "Refresh Interval (seconds)",
    min_value=1,
    max_value=10,
    value=3
)

time_window = st.sidebar.slider(
    "Recent Activity Window (minutes)",
    min_value=1,
    max_value=30,
    value=5
)

customer_filter = st.sidebar.text_input("🔍 Customer ID Lookup")

st.sidebar.divider()
st.sidebar.markdown("**Architecture**")
st.sidebar.markdown("""
```
Kafka → Scoring Service
         ├─ MCP: Customer History
         ├─ MCP: Fraud Rules
         └─ MCP: Explanation
```
""")


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
    st.warning("⏳ Waiting for scoring service to initialize database...")
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
# Helper: Parse triggered_rules JSON
# -----------------------------------

def parse_rules(rules_str):
    """Safely parse triggered_rules JSON string into a list."""
    if not rules_str or pd.isna(rules_str):
        return []
    try:
        return json.loads(rules_str)
    except (json.JSONDecodeError, TypeError):
        return []


def render_rule_badges(rules_list):
    """Render rule names as colored badge HTML."""
    if not rules_list:
        return '<span style="color:#666;">—</span>'
    badges = []
    for rule in rules_list:
        label = rule.replace("_", " ").title()
        badges.append(f'<span class="rule-tag">{label}</span>')
    return " ".join(badges)


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
            AVG(TIMESTAMPDIFF(MICROSECOND, processed_at, created_at))/1000 as avg_db_delay_ms,
            MAX(TIMESTAMPDIFF(MICROSECOND, processed_at, created_at))/1000 as max_db_delay_ms
        FROM scored_transactions
        WHERE processed_at IS NOT NULL
    """
    return pd.read_sql(query, engine)


def load_recent_high_risk(window):
    query = f"""
        SELECT transaction_id, customer_id, amount, country, score,
               mcp_risk_score, triggered_rules, explanation, status, reason,
               created_at
        FROM scored_transactions
        WHERE created_at >= NOW() - INTERVAL {window} MINUTE
        AND score >= 0.65
        ORDER BY score DESC
        LIMIT 50
    """
    return pd.read_sql(query, engine)


def load_top_customers():
    query = """
        SELECT customer_id,
               COUNT(*) as total_tx,
               SUM(CASE WHEN status='DECLINED' THEN 1 ELSE 0 END) as declined_tx,
               SUM(CASE WHEN status='REVIEW' THEN 1 ELSE 0 END) as review_tx,
               ROUND(AVG(score), 4) as avg_score,
               ROUND(AVG(COALESCE(mcp_risk_score, 0)), 1) as avg_mcp_risk
        FROM scored_transactions
        GROUP BY customer_id
        ORDER BY declined_tx DESC, avg_score DESC
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


def load_mcp_rules_distribution():
    """Get distribution of which MCP rules are triggered most often."""
    query = """
        SELECT triggered_rules
        FROM scored_transactions
        WHERE triggered_rules IS NOT NULL
        AND triggered_rules != '[]'
    """
    df = pd.read_sql(query, engine)
    if df.empty:
        return pd.DataFrame(columns=["rule", "count"])

    rule_counts = {}
    for _, row in df.iterrows():
        rules = parse_rules(row["triggered_rules"])
        for rule in rules:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1

    result = pd.DataFrame(
        [{"rule": k, "count": v} for k, v in rule_counts.items()]
    ).sort_values("count", ascending=False)
    return result


def load_country_risk_distribution():
    """Get fraud rate by transaction country."""
    query = """
        SELECT 
            COALESCE(country, 'Unknown') as country,
            COUNT(*) as total_tx,
            SUM(CASE WHEN status IN ('DECLINED', 'REVIEW') THEN 1 ELSE 0 END) as flagged_tx,
            ROUND(AVG(score), 4) as avg_score,
            ROUND(AVG(COALESCE(mcp_risk_score, 0)), 1) as avg_mcp_risk
        FROM scored_transactions
        GROUP BY country
        ORDER BY flagged_tx DESC
    """
    return pd.read_sql(query, engine)


def load_mcp_vs_ml_comparison():
    """Compare ML scores vs MCP risk scores for recent transactions."""
    query = f"""
        SELECT score as final_score,
               mcp_risk_score,
               status, reason
        FROM scored_transactions
        WHERE created_at >= NOW() - INTERVAL {time_window} MINUTE
        AND mcp_risk_score IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 500
    """
    return pd.read_sql(query, engine)


def load_recent_explanations(window, limit=10):
    """Load most recent MCP-generated fraud explanations."""
    query = f"""
        SELECT transaction_id, customer_id, amount, country,
               score, mcp_risk_score, triggered_rules,
               explanation, status, created_at
        FROM scored_transactions
        WHERE created_at >= NOW() - INTERVAL {window} MINUTE
        AND explanation IS NOT NULL
        AND explanation != ''
        ORDER BY score DESC
        LIMIT {limit}
    """
    return pd.read_sql(query, engine)


def load_customer_lifetime(customer_id):
    query = text("""
        SELECT 
            COUNT(*) as total_tx,
            SUM(CASE WHEN status = 'DECLINED' THEN 1 ELSE 0 END) as declined_tx,
            SUM(CASE WHEN status = 'REVIEW' THEN 1 ELSE 0 END) as review_tx,
            ROUND(AVG(score), 4) as avg_score,
            ROUND(AVG(COALESCE(mcp_risk_score, 0)), 1) as avg_mcp_risk
        FROM scored_transactions
        WHERE customer_id = :customer_id
    """)
    return pd.read_sql(query, engine, params={"customer_id": customer_id})


def load_customer_recent_transactions(customer_id, limit=20):
    query = text("""
        SELECT transaction_id, amount, country, score,
               mcp_risk_score, triggered_rules, explanation,
               status, reason, created_at
        FROM scored_transactions
        WHERE customer_id = :customer_id
        ORDER BY created_at DESC
        LIMIT :limit
    """)
    return pd.read_sql(query, engine, params={"customer_id": customer_id, "limit": limit})


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
    st.warning("⏳ No transactions available yet. Waiting for data...")
    st.stop()


# ===================================
# SYSTEM HEALTH PANEL
# ===================================

st.subheader("📊 System Health")

col1, col2, col3, col4, col5 = st.columns(5)

declined = int(totals.loc[totals["status"] == "DECLINED", "total"].sum())
review = int(totals.loc[totals["status"] == "REVIEW", "total"].sum())
approved = int(totals.loc[totals["status"] == "APPROVED", "total"].sum())
total_all = declined + review + approved
tpm = int(throughput_df["tx_last_min"].iloc[0])

col1.metric("🔴 DECLINED", f"{declined:,}")
col2.metric("🟡 REVIEW", f"{review:,}")
col3.metric("🟢 APPROVED", f"{approved:,}")
col4.metric("📦 Total Processed", f"{total_all:,}")
col5.metric("⚡ Tx / Minute", f"{tpm:,}")

# Latency / DB Delay
avg_lat = latency_df["avg_db_delay_ms"].iloc[0]
max_lat = latency_df["max_db_delay_ms"].iloc[0]
if avg_lat is not None:
    lcol1, lcol2 = st.columns(2)
    lcol1.metric("⏱️ Avg DB Queue Delay", f"{avg_lat:.1f} ms")
    lcol2.metric("⏱️ Max DB Queue Delay", f"{max_lat:.1f} ms")

st.divider()

# ===================================
# TABBED SECTIONS
# ===================================

tab_mcp, tab_rules, tab_risk, tab_ops, tab_export = st.tabs([
    "🤖 MCP Intelligence",
    "📜 Rules & Explanations",
    "🔥 Risk Analysis",
    "⚙️ Operations",
    "📦 Export"
])


# -----------------------------------
# TAB 1: MCP Intelligence
# -----------------------------------
with tab_mcp:

    st.subheader("🤖 MCP Enrichment Overview")
    st.markdown(
        "The scoring service queries **three MCP servers** for each transaction: "
        "Customer History, Fraud Rules Engine, and Explanation Service."
    )

    # MCP Rules Distribution Chart
    mcol1, mcol2 = st.columns(2)

    with mcol1:
        st.markdown("#### 🎯 MCP Rules Trigger Frequency")
        rules_dist = load_mcp_rules_distribution()
        if not rules_dist.empty:
            fig_rules = px.bar(
                rules_dist,
                x="rule",
                y="count",
                color="count",
                color_continuous_scale=["#2ec4b6", "#e63946"],
                labels={"rule": "Rule Name", "count": "Times Triggered"},
            )
            fig_rules.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccd6f6",
                showlegend=False,
                xaxis=dict(tickangle=-45),
                height=350,
            )
            fig_rules.update_traces(
                marker_line_color="#0f3460",
                marker_line_width=1,
            )
            st.plotly_chart(fig_rules, use_container_width=True)
        else:
            st.info("No MCP rules have been triggered yet.")

    with mcol2:
        st.markdown("#### 🌍 Risk by Country")
        country_df = load_country_risk_distribution()
        if not country_df.empty:
            fig_country = px.bar(
                country_df,
                x="country",
                y="flagged_tx",
                color="avg_mcp_risk",
                color_continuous_scale=["#2ec4b6", "#ff6b6b", "#e63946"],
                labels={
                    "country": "Country",
                    "flagged_tx": "Flagged Transactions",
                    "avg_mcp_risk": "Avg MCP Risk",
                },
            )
            fig_country.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#ccd6f6",
                height=350,
            )
            st.plotly_chart(fig_country, use_container_width=True)
        else:
            st.info("No country data available yet.")

    # ML vs MCP scatter
    st.markdown("#### ⚖️ ML Score vs MCP Risk Score")
    comparison_df = load_mcp_vs_ml_comparison()
    if not comparison_df.empty and comparison_df["mcp_risk_score"].notna().any():
        fig_scatter = px.scatter(
            comparison_df,
            x="final_score",
            y="mcp_risk_score",
            color="status",
            color_discrete_map={
                "DECLINED": "#e63946",
                "REVIEW": "#f4a261",
                "APPROVED": "#2ec4b6",
            },
            labels={
                "final_score": "Final Blended Score",
                "mcp_risk_score": "MCP Risk Score (0-100)",
            },
            opacity=0.6,
        )
        fig_scatter.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccd6f6",
            height=400,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No MCP comparison data available yet.")

    # Fraud source breakdown (now includes MCP_RULES)
    st.markdown("#### 🧠 Fraud Source Breakdown")
    st.markdown("Shows whether fraud was detected by `ML_MODEL`, `MCP_RULES`, or `VELOCITY_RULE`.")
    if not fraud_source_df.empty:
        fig_source = px.pie(
            fraud_source_df,
            names="reason",
            values="total",
            color="reason",
            color_discrete_map={
                "ML_MODEL": "#4361ee",
                "MCP_RULES": "#e63946",
                "VELOCITY_RULE": "#f4a261",
            },
            hole=0.4,
        )
        fig_source.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccd6f6",
            height=350,
        )
        st.plotly_chart(fig_source, use_container_width=True)

    download_csv(fraud_source_df, "fraud_source_breakdown.csv", "⬇ Export Fraud Source Breakdown")


# -----------------------------------
# TAB 2: Rules & Explanations
# -----------------------------------
with tab_rules:

    st.subheader("📜 MCP Fraud Explanations")
    st.markdown(
        "Human-readable explanations generated by **MCP Server 3** for "
        "flagged transactions (score ≥ 0.65)."
    )

    explanations_df = load_recent_explanations(time_window, limit=15)

    if not explanations_df.empty:
        for _, row in explanations_df.iterrows():
            score = row["score"]
            status = row["status"]
            tx_id = row["transaction_id"][:12] + "..."
            amount = row["amount"]
            country = row.get("country", "—")
            mcp_risk = row.get("mcp_risk_score", 0)
            explanation_text = row.get("explanation", "")
            rules = parse_rules(row.get("triggered_rules", "[]"))

            # Status color
            if status == "DECLINED":
                status_emoji = "🔴"
                css_class = "mcp-explanation"
            elif status == "REVIEW":
                status_emoji = "🟡"
                css_class = "mcp-explanation"
            else:
                status_emoji = "🟢"
                css_class = "mcp-explanation-safe"

            rules_html = render_rule_badges(rules)

            st.markdown(f"""
            <div class="{css_class}">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong>{status_emoji} {status}</strong>
                    <span style="color:#8892b0; font-size:0.8rem;">Tx: {tx_id}</span>
                </div>
                <div style="margin-bottom:6px;">
                    💰 <strong>${amount:,.2f}</strong> &nbsp;|&nbsp;
                    🌍 {country} &nbsp;|&nbsp;
                    📊 Score: <strong>{score:.3f}</strong> &nbsp;|&nbsp;
                    🤖 MCP Risk: <strong>{mcp_risk:.0f}/100</strong>
                </div>
                <div style="margin-bottom:8px;">{rules_html}</div>
                <div style="font-style:italic; color:#a8b2d1;">
                    💬 {explanation_text if explanation_text else "No explanation generated."}
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("No MCP explanations generated yet. Explanations are created for high-risk transactions (score ≥ 0.65).")


# -----------------------------------
# TAB 3: Risk Analysis
# -----------------------------------
with tab_risk:

    st.subheader("🔥 High Risk Transactions")
    high_risk_df = load_recent_high_risk(time_window)
    if not high_risk_df.empty:
        # Format for display
        display_df = high_risk_df.copy()
        if "triggered_rules" in display_df.columns:
            display_df["triggered_rules"] = display_df["triggered_rules"].apply(
                lambda x: ", ".join(parse_rules(x)) if x else "—"
            )
        if "explanation" in display_df.columns:
            display_df["explanation"] = display_df["explanation"].apply(
                lambda x: (x[:80] + "...") if x and len(str(x)) > 80 else (x or "—")
            )
        st.dataframe(display_df, use_container_width=True, height=400)
        download_csv(high_risk_df, "high_risk_transactions.csv", "⬇ Export High Risk Transactions")
    else:
        st.success(f"✅ No high-risk transactions in the last {time_window} minutes.")

    st.divider()

    st.subheader("🚨 Top Risk Customers")
    top_customers = load_top_customers()
    if not top_customers.empty:
        st.dataframe(top_customers, use_container_width=True)
        download_csv(top_customers, "top_risk_customers.csv", "⬇ Export Top Risk Customers")
    else:
        st.info("No customer data available yet.")

    st.divider()

    st.subheader("⚡ Velocity Alerts")
    velocity_df = load_velocity_suspects(time_window)
    if not velocity_df.empty:
        st.dataframe(velocity_df, use_container_width=True)
        download_csv(velocity_df, "velocity_alerts.csv", "⬇ Export Velocity Alerts")
    else:
        st.success(f"✅ No velocity alerts in the last {time_window} minutes.")


# -----------------------------------
# TAB 4: Operations
# -----------------------------------
with tab_ops:

    # Customer Investigation
    st.subheader("🔍 Customer Investigation")

    if customer_filter:
        lifetime_df = load_customer_lifetime(customer_filter)
        if not lifetime_df.empty and lifetime_df["total_tx"].iloc[0] > 0:
            st.markdown(f"**Customer: `{customer_filter}`**")

            icol1, icol2, icol3, icol4, icol5 = st.columns(5)
            icol1.metric("Total Tx", int(lifetime_df["total_tx"].iloc[0]))
            icol2.metric("Declined", int(lifetime_df["declined_tx"].iloc[0]))
            icol3.metric("Review", int(lifetime_df["review_tx"].iloc[0]))
            icol4.metric("Avg Score", f"{lifetime_df['avg_score'].iloc[0]:.4f}")
            icol5.metric("Avg MCP Risk", f"{lifetime_df['avg_mcp_risk'].iloc[0]:.0f}")

            st.markdown("**Recent Transactions:**")
            cust_txs = load_customer_recent_transactions(customer_filter)
            if not cust_txs.empty:
                display_cust = cust_txs.copy()
                if "triggered_rules" in display_cust.columns:
                    display_cust["triggered_rules"] = display_cust["triggered_rules"].apply(
                        lambda x: ", ".join(parse_rules(x)) if x else "—"
                    )
                if "explanation" in display_cust.columns:
                    display_cust["explanation"] = display_cust["explanation"].apply(
                        lambda x: (x[:60] + "...") if x and len(str(x)) > 60 else (x or "—")
                    )
                st.dataframe(display_cust, use_container_width=True, height=350)
        else:
            st.warning(f"No transactions found for customer `{customer_filter}`.")
    else:
        st.info("Enter a Customer ID in the sidebar to investigate.")

    st.divider()

    # Country breakdown table
    st.subheader("🌍 Country Risk Table")
    country_table = load_country_risk_distribution()
    if not country_table.empty:
        country_table["fraud_rate_%"] = (
            country_table["flagged_tx"] / country_table["total_tx"] * 100
        ).round(2)
        st.dataframe(country_table, use_container_width=True)
    else:
        st.info("No country data available yet.")


# -----------------------------------
# TAB 5: Export
# -----------------------------------
with tab_export:

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

    if st.button("📥 Prepare Full Dataset Export"):
        status_filter = None if export_status == "ALL" else export_status
        limit_value = None if export_limit == 0 else export_limit

        full_df = load_full_dataset(limit=limit_value, status=status_filter)

        if not full_df.empty:
            st.success(f"Prepared {len(full_df):,} rows for download.")
            download_csv(
                full_df,
                "full_scored_transactions.csv",
                "⬇ Download Full Dataset"
            )
        else:
            st.warning("No data matches the selected filters.")

    st.divider()

    # Individual section exports
    st.markdown("**Quick Exports:**")
    qcol1, qcol2, qcol3 = st.columns(3)

    with qcol1:
        download_csv(fraud_source_df, "fraud_source_breakdown.csv", "⬇ Fraud Sources")
    with qcol2:
        top_cust = load_top_customers()
        download_csv(top_cust, "top_risk_customers.csv", "⬇ Top Risk Customers")
    with qcol3:
        vel_df = load_velocity_suspects(time_window)
        download_csv(vel_df, "velocity_alerts.csv", "⬇ Velocity Alerts")


# -----------------------------------
# Auto Refresh
# -----------------------------------

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
