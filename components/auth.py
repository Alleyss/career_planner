import streamlit as st
import sqlite3
import hashlib

DATABASE_NAME = "users.db"  # SQLite database file name

def create_user_table():
    """Creates the users table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    """Hashes the password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Registers a new user."""
    create_user_table() # Ensure table exists before registering
    hashed_password = hash_password(password)
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True  # Registration successful
    except sqlite3.IntegrityError:
        return False # Username already exists

def login_user(username, password):
    """Logs in an existing user."""
    create_user_table() # Ensure table exists before login attempt
    hashed_password = hash_password(password)
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user is not None # Returns True if user exists and password matches

def auth_page(): # Renamed to auth_page and made it a function
    st.title("User Authentication")
    auth_status = st.session_state.get('authentication_status')

    if auth_status is None:
        st.session_state['authentication_status'] = False # Initialize if not set

    if not st.session_state['authentication_status']:
        authenticator() # Call authenticator function here
    elif st.session_state['authentication_status']:
        st.write(f"Welcome, {st.session_state['name']}!")
        # You can add logout button or other authenticated content here
    else:
        st.error("Authentication failed")

def authenticator(): # Moved authenticator logic into its own function
    st.subheader("Login or Register")
    auth_choice = st.radio("Choose:", ["Login", "Register"])

    if auth_choice == "Register":
        st.subheader("Register")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Register"):
            if register_user(new_username, new_password):
                st.success("Registration successful. Please log in.")
            else:
                st.error("Username already exists. Please choose another.")

    elif auth_choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.success(f"Logged in as {username}")
                st.session_state['authentication_status'] = True # Set session state on successful login
                st.session_state['name'] = username # Store username in session state
                st.rerun() # Rerun to update UI
            else:
                st.error("Login failed. Incorrect username or password.")

    # if __name__ == "__main__": # Removed from authenticator() to avoid conflict when running auth.py directly


if __name__ == "__main__":
    auth_page() # Call auth_page to display authentication UI when running directly