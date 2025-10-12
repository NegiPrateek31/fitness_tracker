import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# --- Exercise Recommendation Models (using Synthetic Data) ---

def build_synthetic_data(n=300):
    """Generates synthetic data for exercise recommendation training."""
    rng = np.random.RandomState(42)
    bmi = rng.uniform(18, 35, n)
    age = rng.randint(18, 60, n)
    goal = rng.choice([0,1,2], n)
    exercises = ['Walking','Jogging','Push-ups','Plank','Cycling','Squats','Yoga']
    labels = rng.choice(exercises, n)
    df = pd.DataFrame({'bmi':bmi,'age':age,'goal':goal,'exercise':labels})
    return df

def fit_recommender():
    """Trains the base KNN and KMeans models."""
    df = build_synthetic_data(300)
    X = df[['bmi','age','goal']]
    y = df['exercise']
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X,y)
    km = KMeans(n_clusters=3, random_state=42, n_init='auto').fit(X)
    reg = LinearRegression()
    # Note: Calorie predictor is trained separately on user's actual log data
    return {'knn':knn,'kmeans':km,'df':df,'reg':reg}

def recommend_exercises(username, model_data, user_info=None):
    """Recommends exercises based on user profile using KNN."""
    if user_info is None:
        bmi=25; age=30; goal=0
    else:
        bmi = user_info.get('bmi',25)
        age = user_info.get('age',30)
        # Convert goal string to numerical index used in synthetic data (0:Stay Fit, 1:Lose Weight, 2:Gain Muscle)
        goal_map = {'Stay Fit': 0, 'Lose Weight': 1, 'Gain Muscle': 2}
        goal = goal_map.get(user_info.get('goal', 'Stay Fit'), 0)
        
    Xq = [[bmi, age, goal]]
    knn = model_data['knn']
    preds = knn.predict(Xq)
    return list(preds)[:3]

# --- Calorie and Step Prediction Models (using User Log Data) ---

def fit_calorie_predictor(df_user):
    """
    Trains a Random Forest Regressor to predict Calories burned 
    based on steps, water, and sleep.
    """
    # Requires at least 10 data points to train a meaningful model
    if df_user.empty or len(df_user) < 10:
        return None 
    
    # Features for calorie prediction
    FEATURES = ['steps', 'water', 'sleep']
    TARGET = 'calories'
    
    X = df_user[FEATURES]
    y = df_user[TARGET]
    
    # Split for a basic train/test evaluation (optional in a real small-data app)
    # Here we will just use all available data for training for maximum utility.
    
    # Initialize and train the Random Forest Regressor model.
    # RandomForest is robust to non-linear relationships.
    model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X, y)
    
    return model

def predict_next_day_steps_and_calories(username, df_user):
    """
    Predicts the next day's steps (simple average increase) and calories (using ML model).
    """
    # 1. Step Prediction (Simple Trend)
    if df_user.empty:
        predicted_steps = 5000
    else:
        last7 = df_user.tail(7)
        # Predict steps as a 2% increase on the last 7 days' mean, or just the overall mean if less than 7 days
        mean_steps = last7['steps'].mean() if not last7.empty else df_user['steps'].mean()
        predicted_steps = int(mean_steps * 1.02)
    
    # 2. Calorie Prediction (ML Model)
    calorie_model = fit_calorie_predictor(df_user)
    
    if calorie_model is None:
        # Fallback: Simple correlation prediction or average
        if not df_user.empty:
            predicted_calories = int(df_user['calories'].mean())
        else:
            predicted_calories = 300
    else:
        # Use the average of the last few days' inputs for the prediction input
        last_data = df_user[['steps', 'water', 'sleep']].tail(3).mean()
        
        # Create a new data point for tomorrow's prediction
        # We predict using the predicted steps, and the average water/sleep
        X_new = pd.DataFrame({
            'steps': [predicted_steps],
            'water': [last_data['water']],
            'sleep': [last_data['sleep']]
        })
        
        predicted_calories = int(calorie_model.predict(X_new)[0])
        # Ensure predicted calories is not negative or wildly low
        predicted_calories = max(predicted_calories, 100) 
        
    return predicted_steps, predicted_calories

# We'll keep the old simple step prediction function just for backwards compatibility
def predict_next_day_steps(username, df_user):
    # This function is now deprecated, use the combined one in app.py
    if df_user is None or df_user.empty:
        return 5000
    last7 = df_user.tail(7)
    if last7.empty:
        return int(df_user['steps'].mean()) if not df_user.empty else 5000
    return int(last7['steps'].mean() * 1.02)
