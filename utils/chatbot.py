# utils/chatbot.py
import openai
import streamlit as st

def init_chat_history():
    """Initialize chat history in session_state safely."""
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

def get_openai_key():
    """Safely get OpenAI API key from Streamlit secrets."""
    try:
        key = st.secrets["OPENAI_API_KEY"]
        if not key:
            raise ValueError("OPENAI_API_KEY is empty")
        return key
    except KeyError:
        st.warning("OpenAI API key is not set. Chatbot will not work.")
        return None

def chat_with_ai(user_input):
    """Get response from OpenAI GPT model."""
    init_chat_history()  # ensure session_state exists
    key = get_openai_key()
    if not key:
        return "⚠️ OpenAI API key missing. Set it in Streamlit Secrets."

    openai.api_key = key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful fitness coach."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        answer = response['choices'][0]['message']['content'].strip()
        st.session_state['chat_history'].append(("User", user_input))
        st.session_state['chat_history'].append(("AI", answer))
        return answer
    except Exception as e:
        return f"⚠️ Error in AI response: {e}"
