if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def chat_with_ai(user_input):
    key = get_openai_key()
    if not key:
        return "⚠️ OpenAI API key is missing. Please set it in Streamlit Secrets."

    openai.api_key = key
    st.session_state['chat_history'].append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful fitness coach."}] + st.session_state['chat_history'],
            max_tokens=150,
            temperature=0.7,
        )
        answer = response['choices'][0]['message']['content'].strip()
        st.session_state['chat_history'].append({"role": "assistant", "content": answer})
        return answer
    except Exception as e:
        return f"⚠️ Error in AI response: {e}"
