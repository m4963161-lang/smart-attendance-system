import streamlit as st
import requests
import pandas as pd

API_URL = "https://smart-attendance-system-gsut.onrender.com/records"

st.title("📊 Smart Attendance Dashboard")

# Fetch data
res = requests.get(API_URL)
data = res.json()["data"]

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)

    # Download option
    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False),
        "attendance.csv"
    )
else:
    st.warning("No attendance data found")