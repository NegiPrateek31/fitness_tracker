# utils/chatbot.py
import streamlit as st
# Make sure this is installed: pip install huggingface-hub
from huggingface_hub import InferenceClient

# --------------------------- #
# Initialize chat history
# --------------------------- #
def init_chat_history():
    if "chat_history" not in st.session_state:
        # Chat history stores dictionaries with 'role' and 'content' keys
        st.session_state["chat_history"] = []

# --------------------------- #
# Get API Key and Model Instance
# --------------------------- #
def get_huggingface_client():
    # Reads HF_TOKEN from the Streamlit secrets
    api_token = st.secrets.get("HF_TOKEN")
    if not api_token:
        return None
    
    # Model remains Mistral-7B-Instruct-v0.2
    return InferenceClient(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        token=api_token
    )

# --------------------------- #
# Chat function (Using text_generation with robust prompt engineering)
# --------------------------- #
def chat_with_ai(user_input: str) -> str:
    """Send user input to the Hugging Face Inference API using text_generation."""
    if not user_input.strip():
        return "Please enter a question."

    client = get_huggingface_client()
    if client is None:
        return "⚠️ Chatbot client failed to initialize. Please ensure the HF_TOKEN is set in Streamlit secrets."

    system_prompt = (
        "You are FitBot, an expert AI fitness coach. "
        "Provide concise, positive, and practical advice "
        "about exercise, nutrition, and wellness."
    )
    
    # 1. CONSTRUCT THE FULL PROMPT STRING using the reliable Instruct Format
    
    # Start the prompt with the system instruction
    full_prompt = f"<s>[INST] {system_prompt} "
    
    # Add conversation history
    # The Mistral instruct format alternates User and Assistant responses within the [INST] tags
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            full_prompt += f"{msg['content']} [/INST]"
        elif msg["role"] == "assistant":
            full_prompt += f" {msg['content']} </s><s>[INST] "

    # Add the current user input and prime the model for its response
    full_prompt += f"{user_input} [/INST]"


    try:
        # 2. CALL THE CORRECT METHOD: client.text_generation()
        response = client.text_generation(
            prompt=full_prompt, 
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            # Stop sequence helps the model stop cleanly after its turn
            stop_sequences=["</s>", "[INST]"], 
            details=False
        )
        
        reply = response.strip()
        
        # 3. Handle Chat History Update (MUST be done in app.py or here, as text-generation doesn't manage it)
        # Note: The history update logic should ideally be in app.py right after chat_with_ai returns.
        # However, for robustness, we'll return the reply and trust the app.py calling logic.
        
        return reply

    except Exception as e:
        error_str = str(e).lower()
        if "rate limit" in error_str or "too many requests" in error_str:
            return "⚠️ Hugging Face Free Tier rate limit exceeded. Please wait a minute and try again."
        elif "authorization" in error_str or "401" in error_str or "token" in error_str:
            return "⚠️ Hugging Face Token Error: Check your HF_TOKEN for validity and 'read' permission."
        else:
            # Catching the specific error from the previous message, just in case
            if "model" in error_str and "not supported for task" in error_str:
                 return "⚠️ API Task Error: Configuration mismatch. This model is only accessible via text-generation when correctly prompted."
            return f"⚠️ Chatbot encountered an unexpected error: {e}"
