import mysql.connector
import os

token_path = ""

def init_db():
    global token_path

    conn = mysql.connector.connect(host="localhost", user="root", password="djpim!", database="weatherapp", connection_timeout=5)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id INT PRIMARY KEY AUTO_INCREMENT, username TEXT NOT NULL, email TEXT, password TEXT NOT NULL)")
    conn.commit()

    token_path = os.path.join(os.getenv("FLET_APP_STORAGE_DATA"), "token.txt")
    return conn


def create_user(conn, username, email, password):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, password)
    )
    conn.commit()


def get_users(conn, search=None):
    cursor = conn.cursor()
    if search == None:
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    
    cursor.execute("SELECT * FROM users WHERE LOWER(username) LIKE ?", ( "%"+search.lower()+"%",))
    return cursor.fetchall()


def update_user(conn, user_id, name, phone, email):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?",
        (name, phone, email, user_id)
    )
    conn.commit()


def delete_contact_db(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()


def get_token():
    global token_path

    try:
        with open(token_path, "r") as f:
            token = str(f.read().strip())
    except (FileNotFoundError, ValueError):
        token = None
    return token


def set_token(token):
    global token_path

    with open(token_path, "w") as f:
        f.write(str(token))