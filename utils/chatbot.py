# utils/chatbot.py
import streamlit as st
import os
from groq import Groq # Correct top-level import
# REMOVED: from groq.lib.chat_completion import ChatCompletion # INCORRECT/DEPRECATED PATH

# --------------------------- #
# Initialize chat history
# --------------------------- #
def init_chat_history():
    if "chat_history" not in st.session_state:
        # History format: [{'role': 'user', 'content': 'hi'}]
        st.session_state["chat_history"] = []

# --------------------------- #
# Chat function using the Groq SDK
# --------------------------- #
def chat_with_ai(user_input: str) -> str:
    """Send user input to the Groq API and return the reply."""
    if not user_input.strip():
        return "Please enter a question."

    # 1. Configuration
    # Groq API Key should be set in Streamlit secrets as GROQ_API_KEY
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY not found. Please set your Groq API Key in Streamlit secrets."
    
    # Initialize the Groq client
    client = Groq(api_key=GROQ_API_KEY)

    # Use a high-speed, stable model
    MODEL_ID = "llama3-8b-8192" 

    system_prompt = (
        "You are FitBot, an expert AI fitness coach. "
        "Provide concise, positive, and practical advice "
        "about exercise, nutrition, and wellness."
    )

    # 2. Construct Messages for the API
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history from session state
    for message in st.session_state.chat_history:
        messages.append({"role": message["role"], "content": message["content"]})

    # Add the current user prompt
    messages.append({"role": "user", "content": user_input})

    try:
        # 3. Call the Groq Chat Completion API
        # Removed type hint reference to the deprecated ChatCompletion class
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            temperature=0.7,
            max_tokens=256,
        )
        
        reply = response.choices[0].message.content.strip()
        
        return reply

    except Exception as e:
        error_str = str(e)
        if "AuthenticationError" in error_str:
            return "⚠️ Groq Auth Error: Your GROQ_API_KEY is invalid. Please check your key."
        elif "RateLimitError" in error_str:
            return "⚠️ Groq Rate Limit Exceeded. You have hit the free tier limit. Please wait a minute."
        else:
            return f"⚠️ Groq API Error: {e}"
