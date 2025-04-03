import sqlite3
import hashlib

# ✅ Create the database & table (run once)
def create_table():
    conn = sqlite3.connect("news.db")  
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            summary TEXT,
            image TEXT,
            published_date TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

# ✅ Function to Add News to Favorites
def add_favorite(title, url, summary, image, published_date):
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO favorites (title, url, summary, image, published_date) VALUES (?, ?, ?, ?, ?)",
                (title, url, summary, image, published_date))
    conn.commit()
    conn.close()

# ✅ Function to Retrieve Saved News
def get_favorites():
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM favorites")
    favorites = cur.fetchall()
    conn.close()
    return favorites

# ✅ Function to Delete a Saved News Item
def delete_favorite(news_id):
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM favorites WHERE id = ?", (news_id,))
    conn.commit()
    conn.close()

# ✅ Hashing passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Function to Create a User
def create_user(username, password):
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Username already exists

# ✅ Function to Authenticate a User
def authenticate_user(username, password):
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password = cur.fetchone()
    conn.close()
    if stored_password and stored_password[0] == hash_password(password):
        return True
    return False

# ✅ Run once to create tables
create_table()
