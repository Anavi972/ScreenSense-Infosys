import streamlit as st

st.set_page_config(page_title="AI Insights", layout="wide")

st.title("🤖 AI-Powered Insights")

# Check if data exists
if 'summary' not in st.session_state or st.session_state['summary'] is None:
    st.warning("⚠️ Please enter data on main page first")
    st.stop()

summ = st.session_state['summary']

# -------------------------------
# AI-LIKE INSIGHTS (Rule-based for now)
# -------------------------------
st.subheader("🧠 Smart Analysis")

screen_time = summ['Your Screen Time (hrs)']
limit = summ['Combined Recommended Limit (hrs)']

if screen_time > limit:
    st.error("📉 Your screen time is significantly above recommended levels.")

    st.write("### 🔍 Behavioral Insight")
    st.write("Your usage pattern indicates potential overexposure to screen-based activities, which may impact sleep quality and productivity.")

    st.write("### 💡 AI Recommendations")
    st.write("• Reduce usage gradually instead of abruptly")
    st.write("• Introduce device-free time before sleep")
    st.write("• Track usage patterns weekly")

else:
    st.success("📈 Your screen habits are within a healthy range.")

    st.write("### 🔍 Behavioral Insight")
    st.write("Your screen usage is balanced and aligns with recommended limits.")

    st.write("### 💡 AI Recommendations")
    st.write("• Maintain current habits")
    st.write("• Continue monitoring usage")
    st.write("• Take regular eye breaks")

# -------------------------------
# ADVANCED INSIGHT
# -------------------------------
st.subheader("📊 Deep Insight")

difference = screen_time - limit

if difference > 2:
    st.write("⚠️ High deviation from recommended usage detected.")
elif difference > 1:
    st.write("Moderate deviation detected.")
else:
    st.write("Minimal deviation — good control over usage.")

# -------------------------------
# FUTURE PREDICTION (Cool feature)
# -------------------------------
st.subheader("🔮 Predicted Impact")

if screen_time > 4.5:
    st.write("If continued, this pattern may lead to increased fatigue and reduced focus.")
elif screen_time > 3.5:
    st.write("Moderate long-term effects possible if not managed.")
else:
    st.write("No significant long-term impact expected.")
