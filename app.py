import streamlit as st
# --- New Imports for Chatbot ---
from utils.chatbot import init_chat_history, chat_with_ai
# --- End of New Imports ---
from utils.auth import init_db, signup_user, login_user, get_user, add_activity, get_activity_df, get_leaderboard, get_streak, ensure_sample_user, get_raw_activity_df, delete_activity
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
        # If not logged in, this sidebar section serves as the login/signup form
        st.header('Access Portal')
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
                    st.success('Account created. Logging in...')
                    st.session_state['auth'] = {'logged_in': True, 'user': su_user}
                    st.rerun() 
                else:
                    st.error('Username exists.')
    else:
        # If logged in, show user info and logout button
        st.write('Logged in as:', st.session_state['auth']['user'])
        if st.button('Logout'):
            st.session_state['auth'] = {'logged_in': False, 'user': None}
            st.rerun()

    st.markdown('---')
    
# --- Main Content Logic ---

if not st.session_state['auth']['logged_in']:
    
    # =======================================================
    # --- ENHANCED PROJECT OVERVIEW LANDING PAGE ---
    # =======================================================
    
    st.markdown("# 🏋️ FITNESS TRACKER 📊")
    st.markdown("### A Capstone Project by Prateek Negi and Vansh Nagpal")
    
    st.markdown("---")
    
    st.header("🎯 Project Goal: Intelligent Health Personalization")
    st.info(
        """
        The **AI Fitness Tracker** is a full-stack, data-driven application designed to move beyond simple data logging. 
        It integrates secure user management, machine learning models, and a high-performance LLM (Groq) to deliver 
        **real-time health predictions and personalized coaching.**
        """
    )
    
    st.subheader("🧠 Core Machine Learning & AI Features")

    col_ml1, col_ml2, col_ml3 = st.columns(3)

    with col_ml1:
        st.success("1. Exercise Recommendation (Custom ML)")
        st.markdown(
            """
            * **Model Used:** **K-Nearest Neighbors (KNN) Classifier**
            * **Function:** Recommends specific workout types (e.g., Yoga, Cycling) by matching the user's **BMI, Age, and Goal** against a comprehensive synthetic training dataset.
            """
        )

    with col_ml2:
        st.success("2. Health Prediction (Custom ML)")
        st.markdown(
            """
            * **Model Used:** **Random Forest Regressor**
            * **Function:** Predicts the user's optimal **next-day calorie burn** and **step goal** based on their last 7 days of activity, water intake, and sleep quality.
            """
        )
        
    with col_ml3:
        st.success("3. Conversational Coaching (API Integration)")
        st.markdown(
            """
            * **API Used:** **Groq** (Model: `llama-3.1-8b-instant`)
            * **Function:** Provides instant, personalized advice by injecting the user's **BMI, BMR, and Goal** directly into the LLM's system prompt for highly contextual answers.
            """
        )

    st.markdown("---")
    
    st.subheader("⚙️ Implementation Stack")
    st.markdown(
        """
        * **Frontend & Hosting:** Streamlit
        * **Backend & Security:** SQLite Database with Password Hashing (Werkzeug)
        * **Data Analysis & Viz:** Pandas, Plotly (for interactive charts)
        """
    )
    
    st.markdown("---")

    st.subheader("🔑 Access the Dashboard")
    st.info("Log in or sign up using the **Access Portal** in the sidebar.")
    st.code("Demo User: usertest / 1234")

    
else:
    # --- DASHBOARD AND CHAT TABS (LOGGED IN VIEW) ---
    
    # Get user info once here and pass it to the chat function
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

        # NOTE: Using st.columns(4) breaks alignment on small screens, but the st.columns function handles 
        # wrapping gracefully for inputs on modern Streamlit deployments. We will keep it for PC layout quality.
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
        
        # --- CONDITIONAL RENDERING ---
        if df.empty:
            st.info("👋 Welcome! Log your first activity above to see your charts, streaks, and personalized AI predictions.")
        else:
            # Charts and Recommendations
            
            # NOTE: These columns are inside the dashboard tab and will stack on mobile, which is good practice.
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
                
                activity_id_map = dict(zip(df_log['date'], df_log['activity_id']))
                
                dates_to_delete = ['- Select Date to Delete -'] + list(df_log['date'])
                
                # --- FIX: DISPLAYING 1-BASED INDEX ---
                # We use the 'No.' column as the index for display
                df_display = df_log[['No.', 'date', 'steps', 'calories', 'water', 'sleep']].set_index('No.').head(30)
                st.dataframe(df_display, use_container_width=True)
                
                date_to_delete = st.selectbox("Select a date to delete log:", dates_to_delete, key='del_date')
                
                if date_to_delete != '- Select Date to Delete -':
                    id_to_delete = activity_id_map[date_to_delete]
                    
                    if st.button(f'❌ Delete Log for {date_to_delete}'):
                        delete_activity(id_to_delete)
                        st.success(f"Log for {date_to_delete} permanently deleted.")
                        st.rerun()

    # --- Chatbot Content (Tab) ---
   # --- Chatbot Content (Tab) ---
    with chatbot_tab:
        st.title("🤖 AI FitBot")
        
        # 1. FETCH TODAY'S DATA
        today_date = pd.to_datetime('today').strftime('%Y-%m-%d')
        df_raw = get_raw_activity_df(user)
        today_log = df_raw[df_raw['date'] == today_date]
        
        # 2. EXTRACT VALUES (OR USE 0 IF NO LOGS)
        current_steps = int(today_log['steps'].iloc[0]) if not today_log.empty else 0
        current_calories = int(today_log['calories'].iloc[0]) if not today_log.empty else 0
        
        # 3. DEBUG PRINT (This is the key!)
        # This will show a blue box in your app confirming the data is ready.
        st.info(f"🔌 SYSTEM DEBUG: Passing {current_steps} steps and {current_calories} calories to the AI.")

        # 4. UPDATE USER INFO
        user_info['steps'] = current_steps
        user_info['calories'] = current_calories

        # 5. INITIALIZE CHAT
        init_chat_history()
        
        # Display Chat History
        with st.container(height=600): 
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat Input
        if chat_prompt := st.chat_input("Ask a question...", key="chat_input_box"):
            st.session_state.chat_history.append({"role": "user", "content": chat_prompt})
            
            # Send the updated user_info to the AI
            reply = chat_with_ai(chat_prompt, user_info)

            if not reply.startswith("⚠️"):
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
            
            st.rerun()
