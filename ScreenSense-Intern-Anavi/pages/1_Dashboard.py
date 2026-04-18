import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("📊 ScreenSense Dashboard")

if 'summary' not in st.session_state or st.session_state['summary'] is None:
    st.warning("⚠️ Please enter data on main page first")
    st.stop()

summ = st.session_state['summary']

# -------------------------------
# KPI CARDS
# -------------------------------
k1, k2, k3 = st.columns(3)

k1.metric("Your Screen Time", f"{summ['Your Screen Time (hrs)']} hrs")
k2.metric("Recommended Limit", f"{summ['Combined Recommended Limit (hrs)']} hrs")
k3.metric("Users Behind You", f"{summ['Users having lower Screen Time (%)']} %")

# -------------------------------
# BAR CHART
# -------------------------------
chart_data = pd.DataFrame({
    "Type": ["Your Usage", "Recommended"],
    "Hours": [
        summ['Your Screen Time (hrs)'],
        summ['Combined Recommended Limit (hrs)']
    ]
})

st.subheader("📊 Usage Comparison")
st.bar_chart(chart_data.set_index("Type"))

# -------------------------------
# RISK ANALYSIS
# -------------------------------
st.subheader("⚠️ Risk Analysis")

if summ['Your Screen Time (hrs)'] > 4.5:
    st.error("High Risk Zone")
elif summ['Your Screen Time (hrs)'] > 3.5:
    st.warning("Moderate Risk Zone")
else:
    st.success("Safe Zone")
