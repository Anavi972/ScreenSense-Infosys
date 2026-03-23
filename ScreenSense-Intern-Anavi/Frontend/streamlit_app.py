# frontend/streamlit_app.py
import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1"

st.title("Screen-Sense — Interactive")
st.markdown("Fill your data to get personalized recommendations & downloadable report.")

with st.form("input_form"):
    age = st.number_input("Age", min_value=5, max_value=120, value=22)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    device = st.text_input("Primary Device", value="Smartphone")
    total_screen = st.number_input("Avg daily screen time (hrs)", value=5.0, step=0.25)
    edu = st.number_input("Educational time (hrs) — optional", value=2.0, step=0.25)
    rec = st.number_input("Recreational time (hrs) — optional", value=max(0.0, total_screen - 2.0), step=0.25)
    submit = st.form_submit_button("Get Recommendations")

if submit:
    payload = {
        "age": int(age),
        "gender": gender,
        "device": device,
        "avg_daily_screen_time_hr": float(total_screen),
        "educational_hr": float(edu),
        "recreational_hr": float(rec)
    }
    res = requests.post(f"{API_BASE}/predict", json=payload).json()
    st.metric("Personalized Combined Limit (hrs)", res['summary']['Combined Recommended Limit (hrs)'])
    st.subheader("Recommendations")
    for r in res['summary']['Your Screen Time (hrs)'],:
        pass
    # Show recommendations list
    for k, v in res['summary'].items():
        if k == "Users having lower Screen Time (%)":
            st.write(f"Users behind you: **{v}%**")
    st.write("### Actionable Recommendations")
    # build suggestions from exceeded flags
    summary = res['summary']
    recs = []
    if summary['Exceeded Combined Limit']:
        recs.append("Try reducing overall screen time by 30–60 minutes/day.")
        recs.append("Schedule one DND session 1 hour before bedtime.")
    else:
        recs.append("Maintain current habits and monitor weekly.")

    for s in recs:
        st.write("- " + s)

    if st.button("Generate PDF Report"):
        r = requests.post(f"{API_BASE}/report", json=payload).json()
        report_url = r['report_url']
        st.success("Report generated")
        st.markdown(f"[Download report]({report_url})")
