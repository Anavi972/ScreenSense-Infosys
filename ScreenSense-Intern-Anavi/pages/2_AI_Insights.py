import streamlit as st

st.set_page_config(page_title="AI Chatbot", layout="wide")

st.title("🤖 ScreenSense Chatbot")

# Check data
if 'summary' not in st.session_state or st.session_state['summary'] is None:
    st.warning("⚠️ Please enter data on main page first")
    st.stop()

summ = st.session_state['summary']

# -------------------------------
# INIT CHAT HISTORY
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# DISPLAY CHAT HISTORY
# -------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# USER INPUT
# -------------------------------
user_input = st.chat_input("Ask about your screen habits...")

# -------------------------------
# RESPONSE LOGIC (AI-LIKE)
# -------------------------------
def generate_response(user_input):
    user_input = user_input.lower()

    screen_time = summ['Your Screen Time (hrs)']
    limit = summ['Combined Recommended Limit (hrs)']

    if "reduce" in user_input or "improve" in user_input:
        return "Try reducing screen time gradually, especially before bedtime. Start with 30 mins reduction daily."

    elif "risk" in user_input:
        if screen_time > 4.5:
            return "You are in a high-risk zone. This may affect sleep, focus, and eye health."
        elif screen_time > 3.5:
            return "Moderate risk detected. Consider reducing usage slightly."
        else:
            return "Your usage is within a safe range."

    elif "recommend" in user_input:
        return "Follow the 20-20-20 rule, reduce night usage, and take frequent breaks."

    elif "score" in user_input:
        score = max(0, 100 - (screen_time * 10))
        return f"Your screen health score is {score}/100."

    else:
        return f"Your screen time is {screen_time} hrs vs recommended {limit} hrs. Try maintaining a balanced routine."

# -------------------------------
# HANDLE CHAT
# -------------------------------
if user_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response
    response = generate_response(user_input)

    # Store bot response
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        st.markdown(response)
