import streamlit as st
import tempfile
import os
# Import your logic directly from your local files
from recommender import recommendation_system
from report_generator import create_pdf_report 

st.set_page_config(page_title="Screen-Sense", page_icon="📊")

st.title("Screen-Sense — Interactive")
st.markdown("Fill your data to get personalized recommendations & a downloadable report.")

# Initialize session state for the PDF button
if 'summary' not in st.session_state:
    st.session_state['summary'] = None
if 'inputs' not in st.session_state:
    st.session_state['inputs'] = None

with st.form("input_form"):
    age = st.number_input("Age", min_value=5, max_value=120, value=22)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    device = st.selectbox("Primary Device", ["Smartphone", "Laptop", "Tablet", "TV"])
    total_screen = st.number_input("Avg daily screen time (hrs)", value=5.0, step=0.25)
    edu = st.number_input("Educational time (hrs) — optional", value=2.0, step=0.25)
    rec = st.number_input("Recreational time (hrs) — optional", value=max(0.0, total_screen - 2.0), step=0.25)
    submit = st.form_submit_button("Get Recommendations")

if submit:
    # CALL LOGIC DIRECTLY (No FastAPI requests here)
    summary = recommendation_system(age, gender, device, total_screen)
    
    # Store in session state so the PDF button outside the form can see it
    st.session_state['summary'] = summary
    st.session_state['inputs'] = {
        "age": int(age), "gender": gender, "device": device,
        "avg_daily_screen_time_hr": float(total_screen),
        "educational_hr": float(edu), "recreational_hr": float(rec)
    }

# Display Results if summary exists
if st.session_state['summary']:
    summary = st.session_state['summary']
    
    st.divider()
    st.metric("Personalized Combined Limit (hrs)", f"{summary['Combined Recommended Limit (hrs)']} hrs")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Analysis")
        st.write(f"Users with less screen time than you: **{summary['Users having lower Screen Time (%)']}%**")
        
    with col2:
        st.subheader("Status")
        if summary['Exceeded Combined Limit']:
            st.warning("⚠️ Exceeded recommended limit.")
        else:
            st.success("✅ Within safe limits.")

    st.write("### Actionable Recommendations")
    recs = ["Try reducing overall screen time by 30–60 minutes/day.", "Schedule one DND session 1 hour before bedtime."] if summary['Exceeded Combined Limit'] else ["Maintain current habits."]
    for s in recs:
        st.write(f"- {s}")

    # PDF Generation
    st.write("---")
    if st.button("Generate PDF Report"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            report_filename = tmp.name
        
        # Prepare data for PDF
        report_summary = summary.copy()
        report_summary['recommendations'] = recs
        
        create_pdf_report(st.session_state['inputs'], report_summary, report_filename)
        
        with open(report_filename, "rb") as f:
            st.download_button(
                label="📄 Download Your Report",
                data=f,
                file_name=f"Screen_Sense_Report_{age}.pdf",
                mime="application/pdf"
            )
        # Optional: Clean up file
        os.remove(report_filename)
