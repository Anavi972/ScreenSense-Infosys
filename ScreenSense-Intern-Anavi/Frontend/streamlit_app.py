import streamlit as st
import os
import tempfile

# Import your local backend logic directly
from recommender import recommendation_system
from report_generator import create_pdf_report

st.title("Screen-Sense — Interactive")
st.markdown("Fill your data to get personalized recommendations & a downloadable report.")

with st.form("input_form"):
    age = st.number_input("Age", min_value=5, max_value=120, value=22)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    # Changed to selectbox for consistency, but you can change back to text_input if preferred
    device = st.selectbox("Primary Device", ["Smartphone", "Laptop", "Tablet", "TV"]) 
    total_screen = st.number_input("Avg daily screen time (hrs)", value=5.0, step=0.25)
    edu = st.number_input("Educational time (hrs) — optional", value=2.0, step=0.25)
    rec = st.number_input("Recreational time (hrs) — optional", value=max(0.0, total_screen - 2.0), step=0.25)
    submit = st.form_submit_button("Get Recommendations")

if submit:
    # 1. Call the recommendation system directly instead of making an HTTP request
    summary = recommendation_system(
        age=int(age),
        gender=gender.capitalize(),
        device=device.capitalize(),
        screen_time=float(total_screen)
    )
    
    # 2. Display Metrics
    st.metric("Personalized Combined Limit (hrs)", summary['Combined Recommended Limit (hrs)'])
    st.subheader("Recommendations")
    
    # Show user percentiles
    if "Users having lower Screen Time (%)" in summary:
        st.write(f"Users behind you: **{summary['Users having lower Screen Time (%)']}%**")
        
    st.write("### Actionable Recommendations")
    
    # 3. Build suggestions from exceeded flags
    recs = []
    if summary['Exceeded Combined Limit']:
        recs.append("Try reducing overall screen time by 30–60 minutes/day.")
        recs.append("Schedule one DND session 1 hour before bedtime.")
    else:
        recs.append("Maintain current habits and monitor weekly.")

    for s in recs:
        st.write("- " + s)

    # 4. Generate PDF Report locally and provide a download button
    inputs_dict = {
        "age": int(age),
        "gender": gender,
        "device": device,
        "avg_daily_screen_time_hr": float(total_screen),
        "educational_hr": float(edu),
        "recreational_hr": float(rec)
    }
    
    # Create a temporary file to save the PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        temp_filename = tmp_file.name
        
    # Generate the PDF into the temp file
    create_pdf_report(inputs_dict, summary, temp_filename)
    
    # Read the PDF bytes for Streamlit's download button
    with open(temp_filename, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name="Screen_Sense_Personalized_Report.pdf",
        mime="application/pdf"
    )
    
    # Clean up the temporary file from the server/container
    try:
        os.remove(temp_filename)
    except Exception:
        pass
