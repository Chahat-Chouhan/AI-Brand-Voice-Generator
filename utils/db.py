import sqlite3
import hashlib
import json

DB_FILE = "app_database.db"

def init_db():
    """Initializes SQLite database with Users and Chat History tables."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            auth_provider TEXT DEFAULT 'email'
        )
    ''')
    
    # User Chat History table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            brand_name TEXT NOT NULL,
            content_type TEXT NOT NULL,
            topic TEXT NOT NULL,
            generated_copy TEXT NOT NULL,
            chat_logs TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email: str, password: str = None, auth_provider: str = 'email'):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    p_hash = hash_password(password) if password else None
    try:
        c.execute("INSERT INTO users (email, password_hash, auth_provider) VALUES (?, ?, ?)",
                  (email.lower(), p_hash, auth_provider))
        conn.commit()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    p_hash = hash_password(password)
    c.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (email.lower(), p_hash))
    user = c.fetchone()
    conn.close()
    return user is not None

def save_chat_session(user_email: str, brand_name: str, content_type: str, topic: str, generated_copy: str, chat_logs: list):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    chat_logs_json = json.dumps(chat_logs)
    c.execute('''
        INSERT INTO chat_history (user_email, brand_name, content_type, topic, generated_copy, chat_logs)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_email, brand_name, content_type, topic, generated_copy, chat_logs_json))
    conn.commit()
    conn.close()

def get_user_chat_history(user_email: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT id, brand_name, content_type, topic, generated_copy, chat_logs, timestamp
        FROM chat_history WHERE user_email = ? ORDER BY timestamp DESC
    ''', (user_email,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for r in rows:
        history.append({
            "id": r[0],
            "brand_name": r[1],
            "content_type": r[2],
            "topic": r[3],
            "generated_copy": r[4],
            "chat_logs": json.loads(r[5]) if r[5] else [],
            "timestamp": r[6]
        })
    return history