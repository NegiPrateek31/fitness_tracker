# utils/chatbot.py
from openai import OpenAI
import streamlit as st

# Initialize client
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", None))

# Initialize chat history in session state
def init_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# Function to chat with AI using new OpenAI API (>=1.0)
def chat_with_ai(user_input):
    if not client.api_key:
        return "⚠️ Missing API key in Streamlit secrets."

    # Append user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.chat_history,
            temperature=0.7,
        )

        reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        return reply

    except Exception as e:
        return f"⚠️ Error in AI response:\n\n{str(e)}"
