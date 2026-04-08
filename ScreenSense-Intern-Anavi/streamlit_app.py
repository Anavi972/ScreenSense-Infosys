import streamlit as st
import tempfile
import os
# Import your logic directly
from recommender import recommendation_system
from report_generator import create_pdf_report 

st.title("Screen-Sense — Interactive")
st.markdown("Fill your data to get personalized recommendations & a downloadable report.")

with st.form("input_form"):
    age = st.number_input("Age", min_value=5, max_value=120, value=22)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    device = st.selectbox("Primary Device", ["Smartphone", "Laptop", "Tablet", "TV"])
    total_screen = st.number_input("Avg daily screen time (hrs)", value=5.0, step=0.25)
    edu = st.number_input("Educational time (hrs) — optional", value=2.0, step=0.25)
    rec = st.number_input("Recreational time (hrs) — optional", value=max(0.0, total_screen - 2.0), step=0.25)
    submit = st.form_submit_button("Get Recommendations")

if submit:
    # IMPORTANT: We call the function directly, NOT via requests.post()
    summary = recommendation_system(age, gender, device, total_screen)
    
    # Display Results
    st.metric("Personalized Combined Limit (hrs)", summary['Combined Recommended Limit (hrs)'])
    
    st.subheader("Analysis")
    if "Users having lower Screen Time (%)" in summary:
        st.write(f"Users with less screen time than you: **{summary['Users having lower Screen Time (%)']}%**")
        
    st.write("### Actionable Recommendations")
    
    recs = []
    if summary['Exceeded Combined Limit']:
        st.warning("⚠️ You have exceeded the recommended combined limit.")
        recs.append("Try reducing overall screen time by 30–60 minutes/day.")
        recs.append("Schedule one DND session 1 hour before bedtime.")
    else:
        st.success("✅ You are within the safe recommended limit.")
        recs.append("Maintain current habits and monitor weekly.")

    for s in recs:
        st.write("- " + s)

    # Store summary in session state so the PDF button can access it without rerunning logic
    st.session_state['summary'] = summary
    st.session_state['inputs'] = {
        "age": int(age), "gender": gender, "device": device,
        "avg_daily_screen_time_hr": float(total_screen),
        "educational_hr": float(edu), "recreational_hr": float(rec)
    }

# PDF Generation (Outside the submit form to avoid nested button issues)
if 'summary' in st.session_state:
    st.write("---")
    if st.button("Generate PDF Report"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            report_filename = tmp.name
        
        # Add 'recommendations' list to summary for the PDF generator
        report_summary = st.session_state['summary'].copy()
        report_summary['recommendations'] = ["Try reducing screen time", "Schedule DND"] # or dynamic list
        
        create_pdf_report(st.session_state['inputs'], report_summary, report_filename)
        
        with open(report_filename, "rb") as f:
            st.download_button(
                label="📄 Download Your Report",
                data=f,
                file_name=f"Screen_Sense_Report.pdf",
                mime="application/pdf"
            )
