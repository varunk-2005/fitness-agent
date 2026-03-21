import sqlite3
import os
from datetime import datetime

DB_PATH = "fitness_agent.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT 'User',
            age INTEGER,
            weight REAL,
            height REAL,
            goal TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            role TEXT,           -- 'user' or 'assistant'
            content TEXT,
            agent_route TEXT,    -- 'workout', 'nutrition', 'recovery', 'both', 'unknown'
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            date TEXT,
            workout_type TEXT,
            duration_minutes INTEGER,
            notes TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS nutrition_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            date TEXT,
            calories INTEGER,
            protein_g REAL,
            notes TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS recovery_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            date TEXT,
            sleep_hours REAL,
            soreness_level INTEGER,  -- 1 to 5
            notes TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()
    print("Database initialized.")


def save_profile(age, weight, height, goal, name="User"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = 1")
    exists = cursor.fetchone()
    if exists:
        cursor.execute("""
            UPDATE users SET name=?, age=?, weight=?, height=?, goal=?
            WHERE id = 1
        """, (name, age, weight, height, goal))
    else:
        cursor.execute("""
            INSERT INTO users (id, name, age, weight, height, goal)
            VALUES (1, ?, ?, ?, ?, ?)
        """, (name, age, weight, height, goal))
    conn.commit()
    conn.close()

def load_profile():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None



def save_message(role, content, agent_route="unknown", user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO chat_logs (user_id, role, content, agent_route, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, role, content, agent_route, timestamp))
    conn.commit()
    conn.close()

def load_chat_history(user_id=1, limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, agent_route, timestamp
        FROM chat_logs
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def clear_chat_history(user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_logs WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()



def save_workout_log(workout_type, duration_minutes, notes="", user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO workout_logs (user_id, date, workout_type, duration_minutes, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, date, workout_type, duration_minutes, notes))
    conn.commit()
    conn.close()

def load_workout_logs(user_id=1, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, workout_type, duration_minutes, notes
        FROM workout_logs WHERE user_id = ?
        ORDER BY id DESC LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]



def save_nutrition_log(calories, protein_g, notes="", user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO nutrition_logs (user_id, date, calories, protein_g, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, date, calories, protein_g, notes))
    conn.commit()
    conn.close()

def load_nutrition_logs(user_id=1, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, calories, protein_g, notes
        FROM nutrition_logs WHERE user_id = ?
        ORDER BY id DESC LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_recovery_log(sleep_hours, soreness_level, notes="", user_id=1):
    conn = get_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO recovery_logs (user_id, date, sleep_hours, soreness_level, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, date, sleep_hours, soreness_level, notes))
    conn.commit()
    conn.close()

def load_recovery_logs(user_id=1, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, sleep_hours, soreness_level, notes
        FROM recovery_logs WHERE user_id = ?
        ORDER BY id DESC LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]