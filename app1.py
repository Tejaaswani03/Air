import streamlit as st
import pandas as pd
import snowflake.connector

# --------------------------------
# Snowflake Connection (LOCAL)
# --------------------------------
conn = snowflake.connector.connect(
    user="TEJAASWANI03",
    password="Tejaaswani@031105",
    account="HUPVFOF-ER27492",
    warehouse="COMPUTE_WH",
    database="FRAUD_ANALYTICS",
    schema="GOLD"
)

cursor = conn.cursor()

# --------------------------------
# Page Config
# --------------------------------
st.set_page_config(
    page_title="Fraud Analytics Platform",
    layout="wide"
)

# --------------------------------
# Helper Function
# --------------------------------
def load_data(query):
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall(),
                      columns=[c[0] for c in cursor.description])
    return df


# --------------------------------
# Sidebar
# --------------------------------
st.sidebar.title("🔍 Filters")

date_df = load_data("""
SELECT
MIN(DATE(TXN_TIME)) AS MIN_DATE,
MAX(DATE(TXN_TIME)) AS MAX_DATE
FROM FACT_TRANSACTIONS
""")

start_date = st.sidebar.date_input(
    "Start Date",
    date_df["MIN_DATE"][0]
)

end_date = st.sidebar.date_input(
    "End Date",
    date_df["MAX_DATE"][0]
)


loc_df = load_data("""
SELECT DISTINCT LOCATION FROM FACT_TRANSACTIONS
""")

locations = loc_df["LOCATION"].tolist()

location = st.sidebar.multiselect(
    "Location",
    locations,
    default=locations
)

min_amt, max_amt = st.sidebar.slider(
    "Amount Range",
    0, 200000, (0, 200000)
)


# --------------------------------
# Base Query
# --------------------------------
def base_query():

    q = f"""
    FROM FACT_TRANSACTIONS
    WHERE DATE(TXN_TIME)
    BETWEEN '{start_date}' AND '{end_date}'
    AND AMOUNT BETWEEN {min_amt} AND {max_amt}
    """

    if location:
        locs = ",".join([f"'{l}'" for l in location])
        q += f" AND LOCATION IN ({locs})"

    return q


base = base_query()


# --------------------------------
# Title
# --------------------------------
st.title("⚠️ Fraud & Risk Analytics Dashboard")

st.markdown("Real-Time Financial Monitoring System")

st.divider()


# --------------------------------
# KPIs
# --------------------------------
kpi = load_data(f"""
SELECT
COUNT(*) AS TXNS,
SUM(AMOUNT) AS AMT,
COUNT(DISTINCT CUSTOMER_ID) AS CUSTOMERS,
COUNT(ALERT_TYPE) AS ALERTS,
ROUND(AVG(RISK_SCORE),1) AS RISK
{base}
""")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Transactions", int(kpi.TXNS[0]))
c2.metric("Amount", f"₹{kpi.AMT[0]:,.0f}")
c3.metric("Customers", int(kpi.CUSTOMERS[0]))
c4.metric("Alerts", int(kpi.ALERTS[0]))
c5.metric("Avg Risk", kpi.RISK[0])


# --------------------------------
# Charts Row 1
# --------------------------------
st.subheader("📊 Overview")

col1, col2 = st.columns(2)

# Risk Chart
risk = load_data(f"""
SELECT
CASE
 WHEN RISK_SCORE <40 THEN 'Low'
 WHEN RISK_SCORE BETWEEN 40 AND 70 THEN 'Medium'
 ELSE 'High'
END AS RISK,
COUNT(*) CNT
{base}
GROUP BY 1
""")

with col1:
    st.bar_chart(risk, x="RISK", y="CNT")


# Location Alerts
alerts = load_data(f"""
SELECT
LOCATION,
COUNT(ALERT_TYPE) CNT
{base}
GROUP BY 1
""")

with col2:
    st.bar_chart(alerts, x="LOCATION", y="CNT")


# --------------------------------
# Charts Row 2
# --------------------------------
col3, col4 = st.columns(2)

# Trend
trend = load_data(f"""
SELECT
DATE(TXN_TIME) DT,
SUM(AMOUNT) AMOUNT
{base}
GROUP BY 1
ORDER BY 1
""")

with col3:
    st.line_chart(trend, x="DT", y="AMOUNT")


# Buckets
bucket = load_data(f"""
SELECT
CASE
 WHEN AMOUNT<1000 THEN '<1K'
 WHEN AMOUNT<5000 THEN '1K-5K'
 WHEN AMOUNT<10000 THEN '5K-10K'
 ELSE '>10K'
END BUCKET,
COUNT(*) CNT
{base}
GROUP BY 1
""")

with col4:
    st.bar_chart(bucket, x="BUCKET", y="CNT")


# --------------------------------
# Investigation Table
# --------------------------------
st.subheader("📋 Investigation")

detail = load_data(f"""
SELECT
TXN_ID,
TXN_TIME,
CUSTOMER_ID,
ACCOUNT_ID,
LOCATION,
AMOUNT,
RISK_SCORE,
ALERT_TYPE
{base}
ORDER BY TXN_TIME DESC
LIMIT 500
""")

st.dataframe(detail, use_container_width=True)


# --------------------------------
# Export
# --------------------------------
st.download_button(
    "Download Report",
    detail.to_csv(index=False),
    "fraud_report.csv",
    "text/csv"
)
