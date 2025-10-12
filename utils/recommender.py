import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# Dummy recommender for demo purposes
exercise_list = ['Push-ups','Squats','Running','Yoga','Cycling','Plank','Jumping Jacks']

def fit_recommender():
    # In real app, we could fit a collaborative filtering model
    return exercise_list

def recommend_exercises(user, model, user_info):
    # Randomly select exercises based on BMI/goal
    if user_info['goal'] == 'Lose Weight':
        return ['Running','Cycling','Squats']
    elif user_info['goal'] == 'Gain Muscle':
        return ['Push-ups','Squats','Plank']
    else:
        return ['Yoga','Running','Cycling']

def predict_next_day_steps(user, df):
    if df.empty:
        return 5000
    df = df.sort_values('date')
    df['day_index'] = np.arange(len(df))
    X = df[['day_index']]
    y = df['steps']
    model = LinearRegression().fit(X,y)
    return max(0,int(model.predict([[len(df)]])[0]))
