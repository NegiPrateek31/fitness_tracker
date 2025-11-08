# utils/chatbot.py
import streamlit as st
# Make sure this is installed: pip install huggingface-hub
from huggingface_hub import InferenceClient

# --------------------------- #
# Initialize chat history
# --------------------------- #
def init_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

# --------------------------- #
# Get API Key and Model Instance
# --------------------------- #
def get_huggingface_client():
    # Reads HF_TOKEN from the Streamlit secrets
    api_token = st.secrets.get("HF_TOKEN")
    if not api_token:
        # Return None to signal failure
        return None
    
    # Model remains the same (Mistral 7B)
    return InferenceClient(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        token=api_token
    )

# --------------------------- #
# Chat function with error handling (FIXED FOR CONVERSATIONAL TASK)
# --------------------------- #
def chat_with_ai(user_input: str) -> str:
    """Send user input to the Hugging Face Inference API using the conversational task."""
    if not user_input.strip():
        return "Please enter a question."

    client = get_huggingface_client()
    if client is None:
        return "⚠️ Chatbot client failed to initialize. Please ensure the HF_TOKEN is set in Streamlit secrets."

    # 1. Prepare history for the conversational endpoint
    # Extract lists of alternating user and assistant messages
    past_user_inputs = [msg["content"] for msg in st.session_state.chat_history if msg["role"] == "user"]
    generated_responses = [msg["content"] for msg in st.session_state.chat_history if msg["role"] == "assistant"]
    
    # NOTE: System prompts are often ignored by the free conversational API, 
    # but the history and user input are handled correctly.

    try:
        # 2. CALL THE CORRECT ENDPOINT: client.conversational()
        # This resolves the "Model is not supported for task text-generation" error.
        response = client.conversational(
            text=user_input, 
            past_user_inputs=past_user_inputs,
            generated_responses=generated_responses
        )
        
        # 3. Extract the reply from the response object
        reply = response.generated_text.strip()
        
        return reply

    except Exception as e:
        # Generic error fallback
        error_str = str(e).lower()
        if "rate limit" in error_str or "too many requests" in error_str:
            return "⚠️ Hugging Face Free Tier rate limit exceeded. Please wait a minute and try again."
        elif "authorization" in error_str or "401" in error_str or "token" in error_str:
            # Added "token" and "authorization" to catch potential invalid key errors
            return "⚠️ Hugging Face Token Error: Check your HF_TOKEN for validity and 'read' permission."
        else:
            return f"⚠️ Chatbot encountered an unexpected error: {e}"
