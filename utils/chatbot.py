# utils/chatbot.py
import streamlit as st
import os
from groq import Groq 

# --------------------------- #
# Initialize chat history
# --------------------------- #
def init_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

# --------------------------- #
# Chat function using the Groq SDK (MODIFIED TO ACCEPT user_info)
# --------------------------- #
def chat_with_ai(user_input: str, user_info: dict) -> str:
    """Send user input to the Groq API and return the reply."""
    if not user_input.strip():
        return "Please enter a question."

    # 1. Configuration
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY not found. Please set your Groq API Key in Streamlit secrets."
    
    client = Groq(api_key=GROQ_API_KEY)

    # Use a high-speed, stable model
    MODEL_ID = "llama-3.1-8b-instant" 

    # 2. Dynamic System Prompt: Inject user's stats for context
    
    # Extract key stats from user_info (using default values if user is not fully logged in)
    bmi = user_info.get('bmi', 'Unknown')
    bmr = user_info.get('bmr', 'Unknown')
    age = user_info.get('age', 'Unknown')
    gender = user_info.get('gender', 'Unknown')
    goal = user_info.get('goal', 'Unknown')
    
    context_data = (
        f"The user's current profile details are: "
        f"Gender: {gender}, Age: {age}, BMI: {bmi}, "
        f"Estimated BMR: {bmr} Kcal. "
        f"The user's current fitness goal is: '{goal}'. "
        "Tailor all advice, recommendations, and responses specifically to these metrics and goals."
    )
    
    # Final combined system instruction
    system_prompt = (
        f"You are FitBot, an expert AI fitness coach. {context_data}. "
        "Provide concise, positive, and practical advice only. Do not repeat the user's stats back to them unless asked."
    )

    # 3. Construct Messages for the API
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history from session state
    for message in st.session_state.chat_history:
        messages.append({"role": message["role"], "content": message["content"]})

    # Add the current user prompt
    messages.append({"role": "user", "content": user_input})

    try:
        # 4. Call the Groq Chat Completion API
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            temperature=0.7,
        )
        
        reply = response.choices[0].message.content.strip()
        
        return reply

    except Exception as e:
        error_str = str(e)
        if "AuthenticationError" in error_str:
            return "⚠️ Groq Auth Error: Your GROQ_API_KEY is invalid. Please check your key."
        elif "RateLimitError" in error_str:
            return "⚠️ Groq Rate Limit Exceeded. You have hit the free tier limit. Please wait a minute."
        elif "model_not_found" in error_str:
             return "⚠️ Groq Model Error: The model ID is correct but may be temporarily unavailable. Try swapping to 'llama-3.3-70b-versatile' if this persists."
        else:
            return f"⚠️ Groq API Error: {e}"
