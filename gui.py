import streamlit as st
import requests
import pandas as pd

API_URL = "https://smart-attendance-system-gsut.onrender.com"

# Session
if "login" not in st.session_state:
    st.session_state.login = False

# LOGIN
if not st.session_state.login:
    st.title("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

# DASHBOARD
else:
    st.title("📊 Smart Attendance Dashboard")

    if st.button("Logout"):
        st.session_state.login = False

    try:
        res = requests.get(API_URL + "/records")
        data = res.json()["data"]

        if data:
            df = pd.DataFrame(data)

            # 📊 Summary
            st.subheader("📌 Summary")
            st.metric("Total Records", len(df))
            st.metric("Unique Students", df["name"].nunique())

            # 📋 Table
            st.subheader("📋 Attendance Table")
            st.dataframe(df)

            # 📊 Bar Chart
            st.subheader("📊 Attendance Count")
            count = df["name"].value_counts()
            st.bar_chart(count)

            # 🥧 Pie Chart
            st.subheader("🥧 Distribution")
            st.write(count)

        else:
            st.warning("No data found")

    except:
        st.error("API not connected")