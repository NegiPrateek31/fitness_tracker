# utils/chatbot.py
import streamlit as st
# Ensure this is installed: pip install huggingface-hub
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
# Chat function with error handling (Using text_generation with prompt engineering)
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
    
    # 1. CONSTRUCT THE FULL PROMPT STRING using the Mistral Instruct Format
    # This is the reliable method to send chat history via the text-generation endpoint.
    
    # Start the prompt with the system instruction inside the first instruction block
    full_prompt = f"<s>[INST] {system_prompt} "
    
    # Add previous conversation history
    for msg in st.session_state.chat_history:
        # Note: We assume st.session_state.chat_history stores dictionaries with 'role' and 'content'
        if msg["role"] == "user":
            # Close the previous turn and start the new user turn
            full_prompt += f"[/INST]\n\nUser: {msg['content']} [INST] "
        elif msg["role"] == "assistant":
             # This assumes the assistant's content follows the previous instruction block
             # We just append the content, letting the final [/INST] handle the formatting
             full_prompt += f"{msg['content']}"

    # Add the current user input and prepare the model for generation
    # The final " [/INST]" signals the start of the model's response
    # We use a slightly simpler format to avoid unnecessary instruction blocks:
    full_prompt = f"<s>[INST] {system_prompt}. Conversation History: "
    for msg in st.session_state.chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        full_prompt += f"| {role}: {msg['content']} "
        
    full_prompt += f"| User: {user_input} [/INST]"


    try:
        # 2. CALL THE CORRECT METHOD: client.text_generation()
        response = client.text_generation(
            prompt=full_prompt, 
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            # Stop sequence helps the model stop cleanly
            stop_sequences=["User:", "</s>", "[INST]"], 
            details=False
        )
        
        reply = response.strip()
        
        # 3. Handle Chat History Update (MUST be done manually as we are using text-generation)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        
        return reply

    except Exception as e:
        error_str = str(e).lower()
        if "rate limit" in error_str or "too many requests" in error_str:
            return "⚠️ Hugging Face Free Tier rate limit exceeded. Please wait a minute and try again."
        elif "authorization" in error_str or "401" in error_str or "token" in error_str:
            return "⚠️ Hugging Face Token Error: Check your HF_TOKEN for validity and 'read' permission."
        else:
            return f"⚠️ Chatbot encountered an unexpected error: {e}"
