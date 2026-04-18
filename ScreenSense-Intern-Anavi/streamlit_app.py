import streamlit as st
import tempfile
import os
from recommender import recommendation_system
from report_generator import create_pdf_report 
import sys
import os
sys.path.append(os.path.abspath("."))

st.title("Screen-Sense — Interactive")

# Initialize session state so data persists between clicks
if 'summary' not in st.session_state:
    st.session_state['summary'] = None
if 'inputs' not in st.session_state:
    st.session_state['inputs'] = None
if 'recs' not in st.session_state:
    st.session_state['recs'] = []

with st.form("input_form"):
    age = st.number_input("Age", min_value=5, max_value=120, value=22)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    device = st.selectbox("Primary Device", ["Smartphone", "Laptop", "Tablet", "TV"])
    total_screen = st.number_input("Avg daily screen time (hrs)", value=5.0, step=0.25)
    edu = st.number_input("Educational time (hrs) — optional", value=2.0, step=0.25)
    rec = st.number_input("Recreational time (hrs) — optional", value=max(0.0, total_screen - 2.0), step=0.25)
    submit = st.form_submit_button("Get Recommendations")

if submit:
    # Logic Call
    summary = recommendation_system(age, gender, device, total_screen)
    
    # Generate Recommendations
    current_recs = []
    if summary['Exceeded Combined Limit']:
        st.warning("⚠️ You have exceeded the recommended combined limit.")
        current_recs = ["Try reducing overall screen time by 30–60 minutes/day.", "Schedule one DND session 1 hour before bedtime."]
    else:
        st.success("✅ You are within the safe recommended limit.")
        current_recs = ["Maintain current habits and monitor weekly."]

    # Store everything in session state
    st.session_state['summary'] = summary
    st.session_state['recs'] = current_recs
    st.session_state['inputs'] = {
        "age": int(age), "gender": gender, "device": device,
        "avg_daily_screen_time_hr": float(total_screen),
        "educational_hr": float(edu), "recreational_hr": float(rec)
    }

# Display results if they exist in session state
if st.session_state['summary']:
    summ = st.session_state['summary']
    st.metric("Personalized Combined Limit (hrs)", summ['Combined Recommended Limit (hrs)'])
    
    for s in st.session_state['recs']:
        st.write("- " + s)

    st.write("---")
    
    # PDF Generation
    if st.button("Generate PDF Report"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            report_filename = tmp.name
        
        report_summary = st.session_state['summary'].copy()
        report_summary['recommendations'] = st.session_state['recs']
        
        create_pdf_report(st.session_state['inputs'], report_summary, report_filename)
        
        with open(report_filename, "rb") as f:
            st.download_button(
                label="📄 Download Your Report",
                data=f,
                file_name=f"Screen_Sense_Report.pdf",
                mime="application/pdf"
            )
        # Cleanup
        os.remove(report_filename)
