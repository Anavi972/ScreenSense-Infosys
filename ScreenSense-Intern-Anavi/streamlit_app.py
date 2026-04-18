import streamlit as st
import tempfile
import os
import sys

# Fix import path
sys.path.append(os.path.abspath("."))

from recommender import recommendation_system
from report_generator import create_pdf_report 

st.set_page_config(page_title="ScreenSense", layout="wide")

st.markdown("""
# 📱 ScreenSense  
### Smart Screen Time Analyzer & Recommendation System
""")

st.divider()

# -------------------------------
# SESSION STATE INIT
# -------------------------------
if 'summary' not in st.session_state:
    st.session_state['summary'] = None
if 'inputs' not in st.session_state:
    st.session_state['inputs'] = None
if 'recs' not in st.session_state:
    st.session_state['recs'] = []

# -------------------------------
# INPUT FORM
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=5, max_value=120, value=22)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    device = st.selectbox("Primary Device", ["Smartphone", "Laptop", "Tablet", "TV"])

with col2:
    total_screen = st.number_input("Avg daily screen time (hrs)", value=5.0, step=0.25)
    edu = st.number_input("Educational time (hrs)", value=2.0, step=0.25)
    rec = st.number_input("Recreational time (hrs)", value=max(0.0, total_screen - 2.0), step=0.25)

submit = st.button("🚀 Analyze My Screen Usage")

# -------------------------------
# MAIN LOGIC
# -------------------------------
if submit:
    summary = recommendation_system(age, gender, device, total_screen)

    # Recommendations
    current_recs = []
    if summary['Exceeded Combined Limit']:
        st.warning("⚠️ You have exceeded the recommended combined limit.")
        current_recs = [
            "Reduce screen time by 30–60 minutes/day.",
            "Avoid screens 1 hour before bedtime.",
            "Follow 20-20-20 rule for eye care."
        ]
    else:
        st.success("✅ You are within the safe recommended limit.")
        current_recs = ["Maintain current habits and monitor weekly."]

    # Store in session
    st.session_state['summary'] = summary
    st.session_state['recs'] = current_recs
    st.session_state['inputs'] = {
        "age": int(age),
        "gender": gender,
        "device": device,
        "avg_daily_screen_time_hr": float(total_screen),
        "educational_hr": float(edu),
        "recreational_hr": float(rec)
    }

# -------------------------------
# DISPLAY RESULTS
# -------------------------------
if st.session_state['summary']:
    summ = st.session_state['summary']

    st.subheader("📊 Your Report")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Your Screen Time", f"{summ['Your Screen Time (hrs)']} hrs")
        st.metric("Age Limit", f"{summ['Age-based Recommended Limit (hrs)']} hrs")
        st.metric("Device Limit", f"{summ['Device-based Recommended Limit (hrs)']} hrs")

    with col2:
        st.metric("Gender Limit", f"{summ['Gender-based Recommended Limit (hrs)']} hrs")
        st.metric("Combined Limit", f"{summ['Combined Recommended Limit (hrs)']} hrs")
        st.metric("Users Behind (%)", f"{summ['Users having lower Screen Time (%)']} %")

    st.write("### 💡 Recommendations")
    for s in st.session_state['recs']:
        st.write("•", s)

    st.write("---")

    # -------------------------------
    # PDF GENERATION
    # -------------------------------
    if st.button("📄 Generate PDF Report"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            report_filename = tmp.name

        # Add recommendations to summary
        report_summary = summ.copy()
        report_summary['recommendations'] = st.session_state['recs']

        create_pdf_report(
            st.session_state['inputs'],
            report_summary,
            report_filename
        )

        with open(report_filename, "rb") as f:
            st.download_button(
                label="⬇️ Download Your Report",
                data=f,
                file_name="ScreenSense_Report.pdf",
                mime="application/pdf"
            )

        # Cleanup temp file
        os.remove(report_filename)
