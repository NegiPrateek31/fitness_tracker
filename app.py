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

with st.sidebar:
    try:
        st.image('assets/logo.png', use_container_width=True)
    except Exception:
        st.title('AI Fitness Tracker (Logo Missing)')

    st.title('AI Fitness Tracker')
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
                    st.rerun() # Rerun to update the UI immediately after login
                else:
                    st.error('Invalid credentials')
        else:
            su_user = st.text_input('New username', key='su_user')
            su_pwd = st.text_input('New password', type='password', key='su_pwd')
            cols_su = st.columns(2)
            age = cols_su[0].number_input('Age', 10, 100, value=25, key='su_age')
            # MODIFIED: Added Gender select
            gender = cols_su[1].selectbox('Gender', ['M','F'], key='su_gender')
            height = st.number_input('Height (m)', 1.2, 2.2, value=1.7, step=0.01, key='su_height')
            weight = st.number_input('Weight (kg)', 30.0, 200.0, value=70.0, step=0.1, key='su_weight')
            goal = st.selectbox('Goal', ['Stay Fit','Lose Weight','Gain Muscle'], key='su_goal')
            if st.button('Create account'):
                bmi = round(weight/(height*height),2) if height>0 else 0
                # MODIFIED: Passed gender to signup_user
                ok = signup_user(su_user, su_pwd, age, height, weight, bmi, goal, gender)
                if ok:
                    st.success('Account created. Please login.')
                else:
                    st.error('Username exists.')
    else:
        st.write('Logged in as:', st.session_state['auth']['user'])
        if st.button('Logout'):
            st.session_state['auth'] = {'logged_in': False, 'user': None}
            st.rerun() # Rerun to update UI after logout

# --- New Tabbed Interface ---
# Create tabs for the Dashboard and the new Chatbot
dashboard_tab, chatbot_tab = st.tabs(["📊 Dashboard", "🤖 AI FitBot"])

# --- Code for the Dashboard Tab ---
with dashboard_tab:
    st.title('AI Fitness Tracker Dashboard')

    if not st.session_state['auth']['logged_in']:
        st.info('Please login or sign up to see personalized dashboard. Demo user: rohanpal / 1234')
        df_demo = get_activity_df('rohanpal')
        if not df_demo.empty:
            fig = plot_progress(df_demo)
            st.plotly_chart(fig, use_container_width=True)
    else:
        user = st.session_state['auth']['user']
        st.header(f'Welcome, {user} 👋')
        user_info = get_user(user)
        # MODIFIED: Displayed BMR
        st.markdown(f"**BMI:** {user_info['bmi']} | **BMR (Estimated):** {user_info['bmr']} Kcal | **Goal:** {user_info['goal']}")
        st.subheader('Log or Update today\'s activity')
        
        # Check if activity for today exists to prefill and indicate update
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
            st.rerun() # Rerun to refresh charts and data

        st.markdown('---')
        df = get_activity_df(user)
        
        # Display charts in columns for better layout
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            fig = plot_progress(df)
            st.plotly_chart(fig, use_container_width=True)
            
        with chart_col2:
            # MODIFIED: Replaced plot_pie with plot_correlation
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
        
        # --- ADDED SECTION: Manage Logs ---
        st.subheader('Manage Activity Logs')
        df_log = get_raw_activity_df(user)
        
        if df_log.empty:
            st.info("No logs to manage.")
        else:
            st.markdown("Use this section to view or permanently delete past entries.")
            
            # Display only the last 30 entries for cleanliness
            df_display = df_log[['date', 'steps', 'calories', 'water', 'sleep']].head(30)
            st.dataframe(df_display, use_container_width=True)
            
            # Deletion logic
            activity_id_map = dict(zip(df_log['date'], df_log['activity_id']))
            
            # Add a placeholder for a blank option
            dates_to_delete = ['- Select Date to Delete -'] + list(df_log['date'])
            date_to_delete = st.selectbox("Select a date to delete log:", dates_to_delete, key='del_date')
            
            if date_to_delete != '- Select Date to Delete -':
                # Map the date back to the hidden activity_id
                id_to_delete = activity_id_map[date_to_delete]
                
                if st.button(f'❌ Delete Log for {date_to_delete}'):
                    delete_activity(id_to_delete)
                    st.success(f"Log for {date_to_delete} permanently deleted.")
                    st.rerun()
        # --- END OF ADDED SECTION ---


# --- Corrected Code for the Chatbot Tab ---
with chatbot_tab:
    st.title("AI FitBot")
    st.markdown("Your personal AI fitness coach. Ask me anything about exercise, nutrition, or wellness!")

    # REMOVED: Temporary debugging line for the key

    init_chat_history()

    # Display chat messages from history on app rerun
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a fitness question..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant response
        with st.chat_message("assistant"):
            # Call the chat function from your chatbot.py file
            reply = chat_with_ai(prompt)

            # Display the reply (which includes error warnings if they occur)
            st.markdown(reply)

            # Add assistant response to chat history
            # Only append if not an error message
            if not reply.startswith("⚠️"):
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
