import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("✈ Airline Performance & Delay Analytics Dashboard (Local Demo)")

# -------------------------------------------------
# GENERATE SYNTHETIC FLIGHT DATA
# -------------------------------------------------

np.random.seed(42)

airlines = ["AA", "DL", "UA", "SW", "JB"]
airports = ["JFK", "LAX", "ORD", "DFW", "ATL", "BOS"]

data = []

for _ in range(2000):
    month = random.randint(1, 12)
    day_of_week = random.randint(1, 7)
    airline = random.choice(airlines)
    origin = random.choice(airports)
    dest = random.choice(airports)

    departure_delay = np.random.randint(-10, 120)

    airline_delay = max(0, np.random.randint(0, 60))
    weather_delay = max(0, np.random.randint(0, 40))
    late_aircraft_delay = max(0, np.random.randint(0, 50))
    air_system_delay = max(0, np.random.randint(0, 30))
    security_delay = max(0, np.random.randint(0, 10))

    data.append([
        month,
        day_of_week,
        airline,
        origin,
        dest,
        departure_delay,
        airline_delay,
        weather_delay,
        late_aircraft_delay,
        air_system_delay,
        security_delay
    ])

df = pd.DataFrame(data, columns=[
    "MONTH",
    "DAY_OF_WEEK",
    "AIRLINE",
    "ORIGIN_AIRPORT",
    "DESTINATION_AIRPORT",
    "DEPARTURE_DELAY",
    "AIRLINE_DELAY",
    "WEATHER_DELAY",
    "LATE_AIRCRAFT_DELAY",
    "AIR_SYSTEM_DELAY",
    "SECURITY_DELAY"
])

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------

total_flights = len(df)
delayed_flights = len(df[df["DEPARTURE_DELAY"] > 0])
delay_percent = round((delayed_flights / total_flights) * 100, 2)
avg_delay = round(df[df["DEPARTURE_DELAY"] > 0]["DEPARTURE_DELAY"].mean(), 2)

st.markdown("## 📊 Executive KPIs")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Flights", total_flights)
c2.metric("Delayed Flights", delayed_flights)
c3.metric("Delay %", f"{delay_percent}%")
c4.metric("Avg Delay (mins)", avg_delay)

st.divider()

# -------------------------------------------------
# MONTHLY FLIGHT TREND
# -------------------------------------------------

st.markdown("## 📅 Monthly Flight Volume")

monthly = df.groupby("MONTH").size()
st.line_chart(monthly)

st.divider()

# -------------------------------------------------
# MONTHLY DELAY %
# -------------------------------------------------

st.markdown("## 📈 Monthly Delay Percentage")

monthly_delay = df.groupby("MONTH").apply(
    lambda x: (x["DEPARTURE_DELAY"] > 0).sum() * 100 / len(x)
)

st.bar_chart(monthly_delay)

st.divider()

# -------------------------------------------------
# AIRLINE RELIABILITY
# -------------------------------------------------

st.markdown("## 🏆 Airline On-Time Performance")

airline_perf = df.groupby("AIRLINE").apply(
    lambda x: (x["DEPARTURE_DELAY"] <= 0).sum() * 100 / len(x)
)

st.bar_chart(airline_perf)

st.divider()

# -------------------------------------------------
# DELAY CAUSE ANALYSIS
# -------------------------------------------------

st.markdown("## ⚠ Delay Cause Contribution")

delay_causes = df[[
    "AIRLINE_DELAY",
    "WEATHER_DELAY",
    "AIR_SYSTEM_DELAY",
    "LATE_AIRCRAFT_DELAY",
    "SECURITY_DELAY"
]].sum()

st.bar_chart(delay_causes)

st.divider()

# -------------------------------------------------
# AIRPORT PERFORMANCE
# -------------------------------------------------

st.markdown("## 🛫 Average Delay by Origin Airport")

airport_delay = df.groupby("ORIGIN_AIRPORT")["DEPARTURE_DELAY"].mean()

st.bar_chart(airport_delay)

st.divider()

# -------------------------------------------------
# FILTER SECTION
# -------------------------------------------------

st.markdown("## 🔍 Filter by Airline")

selected_airline = st.selectbox("Select Airline", airlines)

filtered_df = df[df["AIRLINE"] == selected_airline]

st.write("Total Flights:", len(filtered_df))
st.write("Delay %:", round(
    (filtered_df["DEPARTURE_DELAY"] > 0).sum() * 100 / len(filtered_df), 2
), "%")

st.dataframe(filtered_df.head(20))