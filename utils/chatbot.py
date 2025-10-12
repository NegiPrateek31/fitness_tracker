# utils/chatbot.py
import openai
import streamlit as st

# Function to safely get OpenAI API key
def get_openai_key():
    try:
        key = st.secrets["OPENAI_API_KEY"]
        if not key:
            raise ValueError("OPENAI_API_KEY is empty")
        return key
    except KeyError:
        st.warning("OpenAI API key not found. Chatbot will not work.")
        return None

# Function to chat with AI
def chat_with_ai(user_input):
    key = get_openai_key()
    if not key:
        return "⚠️ OpenAI API key is missing. Please set it in Streamlit Secrets."
    
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
        return answer
    except Exception as e:
        return f"⚠️ Error in AI response: {e}"
