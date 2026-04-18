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
import google.generativeai as genai

# Configure Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False


def generate_response(user_input):
    screen_time = summ['Your Screen Time (hrs)']
    limit = summ['Combined Recommended Limit (hrs)']

    # -------------------------------
    # USE GEMINI IF AVAILABLE
    # -------------------------------
    if GEMINI_AVAILABLE:
        try:
            prompt = f"""
            You are a smart health assistant.

            User data:
            Screen Time: {screen_time} hrs
            Recommended Limit: {limit} hrs

            User question: {user_input}

            Give a helpful, short, and practical answer.
            """

            response = model.generate_content(prompt)
            return response.text

        except:
            pass  # fallback below

    # -------------------------------
    # FALLBACK (IMPORTANT)
    # -------------------------------
    user_input_lower = user_input.lower()

    if "risk" in user_input_lower:
        if screen_time > 4.5:
            return "High risk: may affect sleep and productivity."
        elif screen_time > 3.5:
            return "Moderate risk detected."
        else:
            return "Low risk: healthy usage."

    return f"Your screen time is {screen_time} hrs vs recommended {limit} hrs."

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
