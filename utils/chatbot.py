# utils/chatbot.py
import streamlit as st
import requests 
import json
import os

# --------------------------- #
# Initialize chat history
# --------------------------- #
def init_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

# --------------------------- #
# Chat function with direct HTTP POST request
# --------------------------- #
def chat_with_ai(user_input: str) -> str:
    """Sends user input via direct HTTP request to the Hugging Face Inference API."""
    if not user_input.strip():
        return "Please enter a question."

    # 1. Configuration
    HF_TOKEN = st.secrets.get("HF_TOKEN")
    if not HF_TOKEN:
        return "⚠️ HF_TOKEN not found. Please set your Hugging Face API Token in Streamlit secrets."

    # --- NEW STABLE MODEL ID ---
    # Using a model ID and endpoint known for better stability on the free tier.
    # The ":hf-inference" suffix often forces routing to a more reliable server.
    MODEL_ID = "openai/gpt-oss-safeguard-20b:hf-inference" 
    API_URL = f"https://router.huggingface.co/models/{MODEL_ID}"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are FitBot, an expert AI fitness coach. "
        "Provide concise, positive, and practical advice "
        "about exercise, nutrition and wellness."
    )

    # 2. CONSTRUCT THE FULL PROMPT STRING (Simple turn-based instruct format)
    full_prompt = f"System: {system_prompt}\n\n"
    
    # Add conversation history
    for msg in st.session_state.chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        full_prompt += f"{role}: {msg['content']}\n"

    # Append the current user input and prime the model for its response
    full_prompt += f"User: {user_input}\nAssistant: "

    # 3. Construct the request payload
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 256,
            "do_sample": True,
            "temperature": 0.7,
            "return_full_text": False, 
            # Stop sequence helps the model stop cleanly after its turn
            "stop_sequences": ["User:", "\n\n"]
        }
    }

    try:
        # 4. Make the direct HTTP POST request
        response = requests.post(API_URL, headers=headers, json=payload, timeout=40) 
        response.raise_for_status() 

        # 5. Process the response
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
            reply = result[0]['generated_text'].strip()
            
            return reply
        
        # Handle model loading or other API errors
        elif isinstance(result, dict) and 'error' in result:
            if 'is currently loading' in result['error']:
                 return f"⚠️ Model is loading. Please wait a moment (est. {result.get('estimated_time', 20):.0f}s) and try again."
            return f"⚠️ Inference Error: {result['error']}"
        
        return "⚠️ Unknown API response format."

    except requests.exceptions.RequestException as e:
        error_str = str(e).lower()
        if "404 client error" in error_str:
             return "⚠️ Network Error: 404. The model endpoint is unavailable. The free router is highly volatile. Please try a different model ID again."
        elif "timeout" in error_str:
            return "⚠️ Request Timed Out. The Hugging Face free server is currently too busy. Please try again later."
        elif "429" in error_str:
            return "⚠️ Rate Limit Exceeded. You have hit the free tier limit. Please wait a few minutes."
        elif "401" in error_str or "unauthorized" in error_str:
            return "⚠️ Authorization Error: Your HF_TOKEN may be incorrect or lack read permission."
        else:
            return f"⚠️ Network Error: {e}"
            
    except Exception as e:
        return f"⚠️ Chatbot encountered an unexpected processing error: {e}"
