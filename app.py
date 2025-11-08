import streamlit as st
# --- New Imports for Chatbot ---
from utils.chatbot import init_chat_history, chat_with_ai
# --- End of New Imports ---
# MODIFIED IMPORTS: Added get_raw_activity_df, delete_activity
from utils.auth import init_db, signup_user, login_user, get_user, add_activity, get_activity_df, get_leaderboard, get_streak, ensure_sample_user, get_raw_activity_df, delete_activity
# MODIFIED IMPORTS: Replaced plot_pie with plot_correlation
from utils.recommender import fit_recommender, recommend_exercises, predict_next_day_steps_and_calories
from utils.charts import plot_progress, plot_correlation, plot_calendar_heatmap 
import pandas as pd

st.set_page_config(page_title='AI Fitness Tracker', layout='wide')
init_db()
ensure_sample_user()

if 'auth' not in st.session_state:
    st.session_state['auth'] = {'logged_in': False, 'user': None}

# --- Sidebar Content (Login/Logout) ---
with st.sidebar:
    try:
        st.image('assets/logo.jpg', use_container_width=True)
    except Exception:
        st.title('AI Fitness Tracker (Logo Missing)')

    st.title('AI Fitness Tracker')
    
    # Login/Logout section
    if not st.session_state['auth']['logged_in']:
        tab = st.selectbox('Choose', ['Login','Sign up'])
        if tab == 'Login':
            user = st.text_input('Username')
            pwd = st.text_input('Password', type='password')
            if st.button('Login'):
                ok = login_user(user, pwd)
                if ok:
                    st.session_state['auth'] = {'logged_in': True, 'user': user}
                    st.success('Logged in')
                    st.rerun()
                else:
                    st.error('Invalid credentials')
        else:
            su_user = st.text_input('New username', key='su_user')
            su_pwd = st.text_input('New password', type='password', key='su_pwd')
            cols_su = st.columns(2)
            age = cols_su[0].number_input('Age', 10, 100, value=25, key='su_age')
            gender = cols_su[1].selectbox('Gender', ['M','F'], key='su_gender')
            height = st.number_input('Height (m)', 1.2, 2.2, value=1.7, step=0.01, key='su_height')
            weight = st.number_input('Weight (kg)', 30.0, 200.0, value=70.0, step=0.1, key='su_weight')
            goal = st.selectbox('Goal', ['Stay Fit','Lose Weight','Gain Muscle'], key='su_goal')
            if st.button('Create account'):
                bmi = round(weight/(height*height),2) if height>0 else 0
                ok = signup_user(su_user, su_pwd, age, height, weight, bmi, goal, gender)
                if ok:
                    st.success('Account created. Please login.')
                else:
                    st.error('Username exists.')
    else:
        st.write('Logged in as:', st.session_state['auth']['user'])
        if st.button('Logout'):
            st.session_state['auth'] = {'logged_in': False, 'user': None}
            st.rerun()

    st.markdown('---')
    
# --- Main Content: Dashboard and Chat Tabs ---
st.title('AI Fitness Tracker Dashboard')

if not st.session_state['auth']['logged_in']:
    st.info('Please login or sign up to see personalized dashboard. Demo user: rohanpal / 1234')
    df_demo = get_activity_df('rohanpal')
    if not df_demo.empty:
        fig = plot_progress(df_demo)
        st.plotly_chart(fig, use_container_width=True)
else:
    # Get user info and create tabs
    user = st.session_state['auth']['user']
    user_info = get_user(user)

    dashboard_tab, chatbot_tab = st.tabs(["📊 Dashboard", "🤖 AI FitBot"])

    # --- Dashboard Content (Tab) ---
    with dashboard_tab:
        
        st.header(f'Welcome, {user} 👋')
        st.markdown(f"**BMI:** {user_info['bmi']} | **BMR (Estimated):** {user_info['bmr']} Kcal | **Goal:** {user_info['goal']}")
        
        st.subheader('Log or Update today\'s activity')
        
        # Activity Logging Logic 
        today_date = pd.to_datetime('today').strftime('%Y-%m-%d')
        df_raw = get_raw_activity_df(user)
        today_log = df_raw[df_raw['date'] == today_date]
        
        current_steps = int(today_log['steps'].iloc[0]) if not today_log.empty else 5000
        current_calories = int(today_log['calories'].iloc[0]) if not today_log.empty else 300
        current_water = float(today_log['water'].iloc[0]) if not today_log.empty else 1.5
        current_sleep = float(today_log['sleep'].iloc[0]) if not today_log.empty else 7.0

        cols = st.columns(4)
        steps = cols[0].number_input('Steps', min_value=0, value=current_steps, step=100)
        calories = cols[1].number_input('Calories burned', min_value=0, value=current_calories, step=10)
        water = cols[2].number_input('Water (L)', min_value=0.0, value=current_water, step=0.1)
        sleep = cols[3].number_input('Sleep hours', min_value=0.0, value=current_sleep, step=0.25)
        
        if st.button('Save/Update entry'):
            add_activity(user, steps, calories, water, sleep)
            st.success('Activity saved or updated!')
            st.rerun()

        st.markdown('---')
        df = get_activity_df(user)
        
        # Charts and Recommendations
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            fig = plot_progress(df)
            st.plotly_chart(fig, use_container_width=True)
            
        with chart_col2:
            fig2 = plot_correlation(df)
            st.plotly_chart(fig2, use_container_width=True)
            
        fig3 = plot_calendar_heatmap(df)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader('AI Recommendations and Predictions')
        
        recommender_models = fit_recommender()
        recs = recommend_exercises(user, recommender_models, user_info)

        predicted_steps, predicted_calories = predict_next_day_steps_and_calories(user, df)

        st.markdown('**Recommended Exercises (Based on Profile):**')
        for r in recs:
            st.write(f'- {r}')

        st.markdown('**Your Predicted Daily Goals:**')
        col_pred1, col_pred2 = st.columns(2)
        col_pred1.info(f'Predicted Steps for Tomorrow: **{predicted_steps:,}**')
        col_pred2.info(f'Predicted Calories to Burn: **{predicted_calories:,}** (Based on your activity trend)')
        
        st.subheader('Streak & Leaderboard')
        streak = get_streak(user)
        st.write(f'🔥 Current active streak: **{streak} days**')
        lb = get_leaderboard()
        st.table(lb)
        
        # Manage Logs section
        st.subheader('Manage Activity Logs')
        df_log = get_raw_activity_df(user)
        
        if df_log.empty:
            st.info("No logs to manage.")
        else:
            st.markdown("Use this section to view or permanently delete past entries.")
            
            df_display = df_log[['date', 'steps', 'calories', 'water', 'sleep']].head(30)
            st.dataframe(df_display, use_container_width=True)
            
            # Deletion logic
            activity_id_map = dict(zip(df_log['date'], df_log['activity_id']))
            
            dates_to_delete = ['- Select Date to Delete -'] + list(df_log['date'])
            date_to_delete = st.selectbox("Select a date to delete log:", dates_to_delete, key='del_date')
            
            if date_to_delete != '- Select Date to Delete -':
                id_to_delete = activity_id_map[date_to_delete]
                
                if st.button(f'❌ Delete Log for {date_to_delete}'):
                    delete_activity(id_to_delete)
                    st.success(f"Log for {date_to_delete} permanently deleted.")
                    st.rerun()

    # --- Chatbot Content (Tab) ---
    with chatbot_tab:
        st.title("🤖 AI FitBot")
        st.markdown("Your personal AI fitness coach. Ask me anything about exercise, nutrition, or wellness!")

        init_chat_history()

        # Create a container to ensure the chat history scrolls and the input stays at the bottom
        chat_container = st.container(height=650)
        
        # 1. DISPLAY CHAT HISTORY
        with chat_container: 
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # 2. CHAT INPUT (Placed directly below the container to stay at the bottom of the tab)
        if chat_prompt := st.chat_input("Ask a question...", key="chat_input_box"):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": chat_prompt})
            
            # Call the Groq-powered backend with user info
            reply = chat_with_ai(chat_prompt, user_info)

            # Add assistant response to history
            if not reply.startswith("⚠️"):
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
            
            # Rerun to update the history display
            st.rerun()
