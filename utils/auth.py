import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
import pandas as pd

DB = os.path.join('data','fitness_users.db')

def calculate_bmr(gender, weight_kg, height_m, age_years):
    """Calculates Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation."""
    height_cm = height_m * 100
    if gender.upper() == 'M':
        # BMR = 10*weight(kg) + 6.25*height(cm) - 5*age(years) + 5
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    elif gender.upper() == 'F':
        # BMR = 10*weight(kg) + 6.25*height(cm) - 5*age(years) - 161
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161
    else:
        # Default to male if gender is unknown or missing
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    return round(bmr, 2)

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # 1. Ensure 'users' table exists with the latest columns
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    age INTEGER,
                    height REAL,
                    weight REAL,
                    bmi REAL,
                    goal TEXT,
                    gender TEXT,
                    bmr REAL
                )''')
                
    # --- SCHEMA MIGRATION: ADD MISSING COLUMNS ---
    # This section ensures backward compatibility and fixes your error.
    
    # Check if 'gender' column exists
    c.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in c.fetchall()]
    
    if 'gender' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN gender TEXT")
    
    # Check if 'bmr' column exists
    if 'bmr' not in columns:
        # We only need the check once, ensuring the BMR column is added if missing
        c.execute("ALTER TABLE users ADD COLUMN bmr REAL")
    
    # 2. Ensure 'activity' table exists
    c.execute('''CREATE TABLE IF NOT EXISTS activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date TEXT,
                    steps INTEGER,
                    calories INTEGER,
                    water REAL,
                    sleep REAL
                )''')
    conn.commit()
    conn.close()

def ensure_sample_user():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    users_to_add = {
        'rohanpal': {'pwd': '1234', 'age': 28, 'height': 1.75, 'weight': 70, 'bmi': 23.0, 'goal': 'Stay Fit', 'gender': 'M', 'step_multiplier': 500, 'base_steps': 4000},
        'fitguru': {'pwd': '1234', 'age': 35, 'height': 1.80, 'weight': 80, 'bmi': 24.7, 'goal': 'Gain Muscle', 'gender': 'M', 'step_multiplier': 800, 'base_steps': 10000},
        'marathoner': {'pwd': '1234', 'age': 45, 'height': 1.65, 'weight': 60, 'bmi': 22.0, 'goal': 'Stay Fit', 'gender': 'F', 'step_multiplier': 1200, 'base_steps': 15000},
        'healthfan': {'pwd': '1234', 'age': 22, 'height': 1.68, 'weight': 55, 'bmi': 19.4, 'goal': 'Lose Weight', 'gender': 'F', 'step_multiplier': 400, 'base_steps': 7500},
        'sleepyhead': {'pwd': '1234', 'age': 50, 'height': 1.72, 'weight': 90, 'bmi': 30.4, 'goal': 'Lose Weight', 'gender': 'M', 'step_multiplier': 100, 'base_steps': 2000},
    }
    
    today = date.today()
    
    for username, data in users_to_add.items():
        c.execute("SELECT id FROM users WHERE username=?", (username,))
        row = c.fetchone()
        
        if not row:
            hashed = generate_password_hash(data['pwd'])
            bmr_val = calculate_bmr(data['gender'], data['weight'], data['height'], data['age'])

            c.execute("INSERT INTO users (username, password, age, height, weight, bmi, goal, gender, bmr) VALUES (?,?,?,?,?,?,?,?,?)",
                      (username, hashed, data['age'], data['height'], data['weight'], data['bmi'], data['goal'], data['gender'], bmr_val))
            user_id = c.lastrowid
            
            for i in range(14):
                d = (today - timedelta(days=13-i)).isoformat()
                
                steps = data['base_steps'] + i * data['step_multiplier']
                calories = 250 + i * 20 + int(data['base_steps'] * 0.05)
                water = 1.5 + (i%3)*0.2
                sleep = 6.5 + (i%4)*0.3
                
                c.execute("INSERT INTO activity (user_id, date, steps, calories, water, sleep) VALUES (?,?,?,?,?,?)",
                          (user_id, d, steps, calories, water, sleep))
                          
    conn.commit()
    conn.close()

def signup_user(username, password, age, height, weight, bmi, goal, gender):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        hashed = generate_password_hash(password)
        bmr = calculate_bmr(gender, weight, height, age)
        c.execute("INSERT INTO users (username, password, age, height, weight, bmi, goal, gender, bmr) VALUES (?,?,?,?,?,?,?,?,?)",
                  (username, hashed, age, height, weight, bmi, goal, gender, bmr))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        return True
    return False

def get_user(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, password, age, height, weight, bmi, goal, gender, bmr FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    keys = ['id','username','password','age','height','weight','bmi','goal', 'gender', 'bmr']
    return dict(zip(keys[:len(row)], row)) 

def add_activity(username, steps, calories, water, sleep):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    user_id = row[0]
    today = date.today().isoformat()
    c.execute("SELECT id FROM activity WHERE user_id=? AND date=?", (user_id, today))
    if c.fetchone():
        c.execute("UPDATE activity SET steps=?, calories=?, water=?, sleep=? WHERE user_id=? AND date=?",
                  (int(steps), int(calories), float(water), float(sleep), user_id, today))
    else:
        # Fixed the INSERT statement to match the columns
        c.execute("INSERT INTO activity (user_id, date, steps, calories, water, sleep) VALUES (?,?,?,?,?,?)",
                (user_id, today, int(steps), int(calories), float(water), float(sleep)))
        
    conn.commit()
    conn.close()

def get_activity_df(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    
    df = pd.DataFrame() 
    
    if row:
        user_id = row[0] 
        df = pd.read_sql_query("SELECT date, steps, calories, water, sleep FROM activity WHERE user_id=? ORDER BY date", conn, params=(user_id,))
    
    conn.close()
    
    if df.empty:
        return df
    
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_raw_activity_df(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    
    df = pd.DataFrame() 
    
    if row:
        user_id = row[0] 
        df = pd.read_sql_query("SELECT id, date, steps, calories, water, sleep FROM activity WHERE user_id=? ORDER BY date DESC", conn, params=(user_id,))
    
    conn.close()
    
    if df.empty:
        return df
    
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d') 
    df = df.rename(columns={'id': 'activity_id'})
    
    # --- FIX: ADD A 1-BASED ROW NUMBER COLUMN ---
    # Calculate the row numbers (1, 2, 3...)
    df.insert(0, 'No.', range(1, 1 + len(df)))
    
    return df

def delete_activity(activity_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM activity WHERE id=?", (activity_id,))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT u.username, SUM(a.steps) as total_steps, COUNT(a.id) as days FROM activity a JOIN users u ON a.user_id=u.id GROUP BY u.username ORDER BY total_steps DESC LIMIT 10", conn)
    conn.close()
    df.index.name = 'Rank'
    df = df.reset_index(drop=False)
    df['Rank'] = df.index + 1
    df = df.set_index('Rank')
    return df

def get_streak(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if not row:
        conn.close()
        return 0
    user_id = row[0]
    c.execute("SELECT date FROM activity WHERE user_id=? ORDER BY date DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return 0
    streak = 0
    today = date.today()
    for i, r in enumerate(rows):
        d = date.fromisoformat(r[0])
        if d == today - timedelta(days=i):
            streak += 1
        else:
            break
    return streak
