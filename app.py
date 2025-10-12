import streamlit as st
from utils.auth import init_db, signup_user, login_user, get_user, add_activity, get_activity_df, get_leaderboard, get_streak, ensure_sample_user
from utils.recommender import fit_recommender, recommend_exercises, predict_next_day_steps_and_calories 
from utils.charts import plot_progress, plot_pie, plot_calendar_heatmap
import pandas as pd

st.set_page_config(page_title='AI Fitness Tracker', layout='wide')
init_db()
ensure_sample_user()

if 'auth' not in st.session_state:
    st.session_state['auth'] = {'logged_in': False, 'user': None}

with st.sidebar:
    # Assuming the logo is available in 'assets/logo.png'
    try:
        st.image('assets/logo.png', use_column_width=True)
    except FileNotFoundError:
        st.title('AI Fitness Tracker') # Fallback if logo not found
        
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
                else:
                    st.error('Invalid credentials')
        else:
            su_user = st.text_input('New username', key='su_user')
            su_pwd = st.text_input('New password', type='password', key='su_pwd')
            age = st.number_input('Age', 10, 100, value=25, key='su_age')
            height = st.number_input('Height (m)', 1.2, 2.2, value=1.7, step=0.01, key='su_height')
            weight = st.number_input('Weight (kg)', 30.0, 200.0, value=70.0, step=0.1, key='su_weight')
            goal = st.selectbox('Goal', ['Stay Fit','Lose Weight','Gain Muscle'], key='su_goal')
            if st.button('Create account'):
                bmi = round(weight/(height*height),2) if height>0 else 0
                ok = signup_user(su_user, su_pwd, age, height, weight, bmi, goal)
                if ok:
                    st.success('Account created. Please login.')
                else:
                    st.error('Username exists.')
    else:
        st.write('Logged in as:', st.session_state['auth']['user'])
        if st.button('Logout'):
            st.session_state['auth'] = {'logged_in': False, 'user': None}

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
    st.markdown(f"**BMI:** {user_info['bmi']}  |  **Goal:** {user_info['goal']}")
    st.subheader('Log today activity')
    cols = st.columns(4)
    steps = cols[0].number_input('Steps', min_value=0, value=5000, step=100)
    calories = cols[1].number_input('Calories burned', min_value=0, value=300, step=10)
    water = cols[2].number_input('Water (L)', min_value=0.0, value=1.5, step=0.1)
    sleep = cols[3].number_input('Sleep hours', min_value=0.0, value=7.0, step=0.25)
    if st.button('Save entry'):
        add_activity(user, steps, calories, water, sleep)
        st.success('Saved!')

    st.markdown('---')
    df = get_activity_df(user)
    fig = plot_progress(df)
    st.plotly_chart(fig, use_container_width=True)
    fig2 = plot_pie(df)
    st.plotly_chart(fig2, use_container_width=True)
    fig3 = plot_calendar_heatmap(df)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader('AI Recommendations and Predictions')
    
    # Train the basic recommender models
    recommender_models = fit_recommender() 
    recs = recommend_exercises(user, recommender_models, user_info)
    
    # Run the combined prediction model
    predicted_steps, predicted_calories = predict_next_day_steps_and_calories(user, df) 

    # Display Recommendations
    st.markdown('**Recommended Exercises (Based on Profile):**')
    for r in recs:
        st.write(f'- {r}')
        
    # Display Predictions
    st.markdown('**Your Predicted Daily Goals:**')
    col_pred1, col_pred2 = st.columns(2)
    col_pred1.info(f'Predicted Steps for Tomorrow: **{predicted_steps:,}**')
    col_pred2.info(f'Predicted Calories to Burn: **{predicted_calories:,}** (Based on your activity trend)') 

    st.subheader('Streak & Leaderboard')
    streak = get_streak(user)
    st.write(f'🔥 Current active streak: **{streak} days**')
    lb = get_leaderboard()
    st.table(lb)
