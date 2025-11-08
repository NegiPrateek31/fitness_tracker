import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# --- Exercise Recommendation Models (using Synthetic Data) ---

def build_synthetic_data(n=5000): # INCREASED SIZE FOR ROBUSTNESS
    """Generates synthetic data for exercise recommendation training."""
    rng = np.random.RandomState(42)
    bmi = rng.uniform(18, 35, n)
    age = rng.randint(18, 60, n)
    goal = rng.choice([0,1,2], n)
    # Added more variety
    exercises = ['Walking','Jogging','Push-ups','Plank','Cycling','Squats','Yoga','Weight Lifting', 'Running', 'Swimming', 'Hiking'] 
    labels = rng.choice(exercises, n)
    df = pd.DataFrame({'bmi':bmi,'age':age,'goal':goal,'exercise':labels})
    return df

def fit_recommender():
    """Trains the base KNN and KMeans models."""
    df = build_synthetic_data(5000) # INCREASED SIZE FOR ROBUSTNESS
    X = df[['bmi','age','goal']]
    y = df['exercise']
    # NOTE: Set n_neighbors to a value > 1 (e.g., 5) to use the kneighbors method later
    knn = KNeighborsClassifier(n_neighbors=5) 
    knn.fit(X,y)
    km = KMeans(n_clusters=3, random_state=42, n_init='auto').fit(X)
    reg = LinearRegression()
    return {'knn':knn,'kmeans':km,'df':df,'reg':reg}

# --- FIX: USE kneighbors TO GET MULTIPLE CLOSEST MATCHES ---
def recommend_exercises(username, model_data, user_info=None):
    """Recommends exercises based on user profile using KNN."""
    if user_info is None:
        bmi=25; age=30; goal=0
    else:
        bmi = user_info.get('bmi',25)
        age = user_info.get('age',30)
        goal_map = {'Stay Fit': 0, 'Lose Weight': 1, 'Gain Muscle': 2}
        goal = goal_map.get(user_info.get('goal', 'Stay Fit'), 0)
        
    Xq = [[bmi, age, goal]]
    knn = model_data['knn']
    
    # Use kneighbors to get the indices of the 3 nearest neighbors
    # n_neighbors is 5, but we only need 3 results.
    distances, indices = knn.kneighbors(Xq, n_neighbors=3)
    
    # Retrieve the corresponding exercise labels using the indices
    df = model_data['df']
    recommended_exercises = df.iloc[indices[0]]['exercise'].unique().tolist()
    
    return recommended_exercises[:3]
# -----------------------------------------------------------


# ... (rest of the file remains unchanged)
def fit_calorie_predictor(df_user):
    # ... (code remains unchanged)
    
def predict_next_day_steps_and_calories(username, df_user):
    # ... (code remains unchanged)
