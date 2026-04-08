import streamlit as st
import os
import tempfile
# Import your logic directly from the files in your root folder
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
    # 1. Direct call to recommender logic (No 'requests' needed)
    summary = recommendation_system(
        age=int(age),
        gender=gender.capitalize(),
        device=device.capitalize(),
        screen_time=float(total_screen)
    )
    
    # 2. Display Metrics
    st.metric("Personalized Combined Limit (hrs)", summary['Combined Recommended Limit (hrs)'])
    
    st.subheader("Analysis")
    if "Users having lower Screen Time (%)" in summary:
        st.write(f"Users with less screen time than you: **{summary['Users having lower Screen Time (%)']}%**")
        
    st.write("### Actionable Recommendations")
    
    # 3. Logic based on results
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

    # 4. Local PDF Generation
    st.write("---")
    if st.button("Generate PDF Report"):
        inputs_payload = {
            "age": int(age),
            "gender": gender,
            "device": device,
            "avg_daily_screen_time_hr": float(total_screen),
            "educational_hr": float(edu),
            "recreational_hr": float(rec)
        }
        
        # Create a temp file to store the generated PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            report_filename = tmp.name
        
        # Call report generator directly
        create_pdf_report(inputs_payload, summary, report_filename)
        
        # Streamlit Download Button
        with open(report_filename, "rb") as f:
            st.download_button(
                label="📄 Download Your Report",
                data=f,
                file_name=f"Screen_Sense_Report_{age}.pdf",
                mime="application/pdf"
            )
        
        # Optional: cleanup the temp file after download button is rendered
        os.unlink(report_filename)
