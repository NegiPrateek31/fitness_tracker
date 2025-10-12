# utils/chatbot.py
import streamlit as st
import google.generativeai as genai

# --------------------------- #
# Initialize chat history
# --------------------------- #
def init_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

# --------------------------- #
# Get compatible model
# --------------------------- #
def get_compatible_model():
    """Return the first available model that supports generateContent."""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found in Streamlit secrets!")
        st.stop()

    genai.configure(api_key=api_key)

    try:
        models = genai.list_models()
        # Filter models that support text generation
        compatible = [m for m in models if "generateContent" in m.supported_generation_methods]
        if not compatible:
            st.error("⚠️ No compatible models found for this API key.")
            st.stop()
        # Prefer latest Gemini 1.5-flash if available
        for m in compatible:
            if "gemini-1.5-flash" in m.name:
                return genai.GenerativeModel(m.name)
        # Otherwise return the first compatible model
        return genai.GenerativeModel(compatible[0].name)
    except Exception as e:
        st.error(f"⚠️ Failed to list models: {e}")
        st.stop()

# --------------------------- #
# Chat function
# --------------------------- #
def chat_with_ai(user_input: str) -> str:
    """Send user input to Gemini AI and return reply."""
    if not user_input.strip():
        return "Please enter a question."

    try:
        model = get_compatible_model()
        system_prompt = (
            "You are FitBot, an expert AI fitness coach. "
            "Provide concise, positive, and practical advice "
            "about exercise, nutrition, and wellness."
        )
        prompt = f"{system_prompt}\n\nUser: {user_input}"

        response = model.generate_content(prompt)
        reply = response.text.strip() if response and response.text else "Sorry, I didn’t catch that."

        # Save to chat history
        st.session_state["chat_history"].append({"user": user_input, "assistant": reply})
        return reply
    except Exception as e:
        return f"⚠️ AI Error: {e}"
