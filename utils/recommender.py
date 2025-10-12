import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

def build_synthetic_data(n=300):
    rng = np.random.RandomState(42)
    bmi = rng.uniform(18, 35, n)
    age = rng.randint(18, 60, n)
    goal = rng.choice([0,1,2], n)
    exercises = ['Walking','Jogging','Push-ups','Plank','Cycling','Squats','Yoga']
    labels = rng.choice(exercises, n)
    df = pd.DataFrame({'bmi':bmi,'age':age,'goal':goal,'exercise':labels})
    return df

def fit_recommender():
    df = build_synthetic_data(300)
    X = df[['bmi','age','goal']]
    y = df['exercise']
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X,y)
    km = KMeans(n_clusters=3, random_state=42).fit(X)
    reg = LinearRegression()
    return {'knn':knn,'kmeans':km,'df':df,'reg':reg}

def recommend_exercises(username, model_data, user_info=None):
    if user_info is None:
        bmi=25; age=30; goal=0
    else:
        bmi = user_info.get('bmi',25)
        age = user_info.get('age',30)
        goal = 0 if user_info.get('goal','Stay Fit')=='Stay Fit' else (1 if user_info.get('goal')=='Lose Weight' else 2)
    Xq = [[bmi, age, goal]]
    knn = model_data['knn']
    preds = knn.predict(Xq)
    return list(preds)[:3]

def predict_next_day_steps(username, df_user):
    if df_user is None or df_user.empty:
        return 5000
    last7 = df_user.tail(7)
    if last7.empty:
        return int(df_user['steps'].mean()) if not df_user.empty else 5000
    return int(last7['steps'].mean() * 1.02)
