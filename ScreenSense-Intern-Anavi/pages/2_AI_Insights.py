import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Chatbot", layout="wide")

st.title("🤖 ScreenSense Chatbot")

# -------------------------------
# CHECK DATA
# -------------------------------
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
# GEMINI SETUP
# -------------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ correct model
    GEMINI_AVAILABLE = True
except Exception as e:
    st.error(f"Gemini init error: {e}")
    GEMINI_AVAILABLE = False

# Debug (remove later)
st.caption(f"Gemini Available: {GEMINI_AVAILABLE}")

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
# RESPONSE FUNCTION
# -------------------------------
def generate_response(user_input):
    screen_time = summ['Your Screen Time (hrs)']
    limit = summ['Combined Recommended Limit (hrs)']

    # -------------------------------
    # GEMINI RESPONSE
    # -------------------------------
    if GEMINI_AVAILABLE:
        try:
            prompt = f"""
            You are a smart and friendly health assistant.

            User data:
            - Screen Time: {screen_time} hrs
            - Recommended Limit: {limit} hrs

            User question: {user_input}

            Give a natural, conversational, and helpful answer.
            """

            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            st.error(f"Gemini runtime error: {e}")

    # -------------------------------
    # FALLBACK LOGIC
    # -------------------------------
    user_input_lower = user_input.lower()

    if "hello" in user_input_lower or "hi" in user_input_lower:
        return "Hey! 👋 I can help you understand and improve your screen habits."

    if "risk" in user_input_lower:
        if screen_time > 4.5:
            return "High risk: may affect sleep, eye health, and productivity."
        elif screen_time > 3.5:
            return "Moderate risk detected."
        else:
            return "Low risk: healthy usage."

    if "improve" in user_input_lower or "reduce" in user_input_lower:
        return "Try reducing screen time gradually, especially before sleep. Start with 30 minutes less per day."

    return f"Your screen time is {screen_time} hrs vs recommended {limit} hrs."

# -------------------------------
# HANDLE CHAT
# -------------------------------
if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response
    response = generate_response(user_input)

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        st.markdown(response)
