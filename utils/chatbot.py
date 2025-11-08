# utils/chatbot.py
import streamlit as st
import requests # New dependency needed
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

    # Use the public Inference API URL for the model
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are FitBot, an expert AI fitness coach. "
        "Provide concise, positive, and practical advice "
        "about exercise, nutrition, and wellness."
    )

    # 2. CONSTRUCT THE FULL PROMPT STRING (Mistral Instruct Format)
    
    # Start the prompt with the system instruction inside the first instruction block
    full_prompt = f"<s>[INST] {system_prompt} "
    
    # Add conversation history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            full_prompt += f"{msg['content']} [/INST]"
        elif msg["role"] == "assistant":
            # Close the instruction block with the assistant's response and start a new block
            full_prompt += f" {msg['content']} </s><s>[INST] "

    # Add the current user input and prime the model for its response
    full_prompt += f"{user_input} [/INST]"
    
    # 3. Construct the request payload
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 256,
            "do_sample": True,
            "temperature": 0.7,
            "return_full_text": False, # Crucial: Only returns the generated response, not the whole prompt
            "stop_sequences": ["</s>", "[INST]"]
        }
    }

    try:
        # 4. Make the direct HTTP POST request
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30) # Added timeout
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Process the response
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
            reply = result[0]['generated_text'].strip()
            
            return reply
        
        # Handle case where model is loading (common in free tier)
        elif isinstance(result, dict) and 'error' in result and 'is currently loading' in result['error']:
            return f"⚠️ Model is loading. Please wait a moment (est. {result.get('estimated_time', 20):.0f}s) and try again."
        
        elif isinstance(result, dict) and 'error' in result:
             return f"⚠️ Inference Error: {result['error']}"
        
        return "⚠️ Unknown API response format."


    except requests.exceptions.RequestException as e:
        error_str = str(e).lower()
        if "timeout" in error_str:
            return "⚠️ Request Timed Out. The Hugging Face free server is currently too busy. Please try again later."
        elif "429" in error_str:
            return "⚠️ Rate Limit Exceeded. You have hit the free tier limit. Please wait a few minutes."
        elif "401" in error_str or "unauthorized" in error_str:
            return "⚠️ Authorization Error: Your HF_TOKEN may be incorrect or lack read permission."
        else:
            return f"⚠️ Network Error: {e}"
            
    except Exception as e:
        return f"⚠️ Chatbot encountered an unexpected processing error: {e}"
