import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
import pandas as pd

# ✅ Streamlit-safe database path (absolute, works both locally and on cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "../data/fitness_users.db")

def init_db():
    """Initialize the SQLite database with tables for users and activity."""
    os.makedirs(os.path.join(BASE_DIR, "../data"), exist_ok=True)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    age INTEGER,
                    height REAL,
                    weight REAL,
                    bmi REAL,
                    goal TEXT
                )''')
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
    """Ensure a sample user (rohanpal) exists with demo activity data."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", ('rohanpal',))
    row = c.fetchone()
    if not row:
        hashed = generate_password_hash('1234')
        c.execute("INSERT INTO users (username, password, age, height, weight, bmi, goal) VALUES (?,?,?,?,?,?,?)",
                  ('rohanpal', hashed, 28, 1.75, 70, 23.0, 'Stay Fit'))
        user_id = c.lastrowid
        today = date.today()
        for i in range(14):
            d = (today - timedelta(days=13 - i)).isoformat()
            steps = 4000 + i * 500
            calories = 250 + i * 20
            water = 1.5 + (i % 3) * 0.2
            sleep = 6.5 + (i % 4) * 0.3
            c.execute("INSERT INTO activity (user_id, date, steps, calories, water, sleep) VALUES (?,?,?,?,?,?)",
                      (user_id, d, steps, calories, water, sleep))
        conn.commit()
    conn.close()

def signup_user(username, password, age, height, weight, bmi, goal):
    """Register a new user into the database."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        hashed = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password, age, height, weight, bmi, goal) VALUES (?,?,?,?,?,?,?)",
                  (username, hashed, age, height, weight, bmi, goal))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Validate a user's login credentials."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        return True
    return False

def get_user(username):
    """Retrieve a user's profile details as a dictionary."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    keys = ['id', 'username', 'password', 'age', 'height', 'weight', 'bmi', 'goal']
    return dict(zip(keys, row))

def add_activity(username, steps, calories, water, sleep):
    """Add a daily activity record for a user."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    user_id = row[0]
    today = date.today().isoformat()
    c.execute("INSERT INTO activity (user_id, date, steps, calories, water, sleep) VALUES (?,?,?,?,?,?)",
              (user_id, today, int(steps), int(calories), float(water), float(sleep)))
    conn.commit()
    conn.close()

def get_activity_df(username):
    """Return all user activity data as a Pandas DataFrame."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if not row:
        conn.close()
        return pd.DataFrame()
    user_id = row[0]
    df = pd.read_sql_query("SELECT date, steps, calories, water, sleep FROM activity WHERE user_id=? ORDER BY date",
                           conn, params=(user_id,))
    conn.close()
    if df.empty:
        return df
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_leaderboard():
    """Return the top 10 users by total steps."""
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("""
        SELECT u.username, SUM(a.steps) as total_steps, COUNT(a.id) as days
        FROM activity a JOIN users u ON a.user_id = u.id
        GROUP BY u.username
        ORDER BY total_steps DESC
        LIMIT 10
    """, conn)
    conn.close()
    return df

def get_streak(username):
    """Calculate the user's current activity streak in days."""
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
