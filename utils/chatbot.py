# utils/chatbot.py
import google.generativeai as genai
import streamlit as st

# --------------------------- #
# Initialize Gemini Chatbot
# --------------------------- #

def init_chat_history():
    """Initialize chat history in session_state if not present."""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

def get_model():
    """Load and configure Gemini model using Streamlit secrets."""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ Gemini API key missing! Add GEMINI_API_KEY in Streamlit secrets.")
        st.stop()

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

# --------------------------- #
# Chat Function
# --------------------------- #

def chat_with_ai(user_input: str) -> str:
    """Send user input to Gemini and return its reply."""
    try:
        model = get_model()
        prompt = (
            "You are FitBot, an expert AI fitness and wellness assistant. "
            "Be friendly, concise, and motivational while helping users with "
            "fitness, diet, and health advice.\n\n"
            f"User: {user_input}"
        )

        response = model.generate_content(prompt)

        # Extract reply safely
        reply = response.text.strip() if response and response.text else "Sorry, I didn’t quite catch that."

        # Store in chat history
        st.session_state["chat_history"].append({"user": user_input, "assistant": reply})

        return reply

    except Exception as e:
        st.error(f"⚠️ AI Error: {e}")
        return "AI service is currently unavailable."
