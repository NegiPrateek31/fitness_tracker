import openai
import os

# Load OpenAI key from Streamlit secrets or environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_ai(user_message: str) -> str:
    """
    Handles conversation with OpenAI API for fitness guidance.
    Returns a smart and motivating response.
    """

    if not openai.api_key:
        return "⚠️ OpenAI API key not found. Please configure it in Streamlit secrets."

    try:
        # Send message to GPT model
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly and knowledgeable AI fitness coach."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=250,
            temperature=0.8
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error: {str(e)}"
