import sqlite3
import json

DATABASE_NAME = "career_plans.db" # SQLite database file for career plans


def connect_to_sqlite():
    """Connects to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    print("Successfully connected to SQLite database!")
    return conn

def create_career_plans_table(conn):
    """Creates the career_plans table if it doesn't exist, with checkbox_states column."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_plans_sqlite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            career_goal TEXT NOT NULL UNIQUE, 
            roadmap_json TEXT NOT NULL,
            checkbox_states TEXT,          
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, career_goal)  
        )
    """)
    conn.commit()
    print("Career plans table created (or already exists), with checkbox_states column.")


def store_roadmap_sqlite(conn, user_id, career_goal, roadmap_json):
    """Stores the generated career roadmap in SQLite database and initializes checkbox_states."""
    create_career_plans_table(conn) # Ensure table exists
    cursor = conn.cursor()
    try:
        roadmap_json_str = json.dumps(roadmap_json) # Convert JSON object to string before storing
        checkbox_states_json_str = json.dumps({}) # Initialize checkbox_states as empty JSON object
        cursor.execute("INSERT INTO career_plans_sqlite (user_id, career_goal, roadmap_json, checkbox_states) VALUES (?, ?, ?, ?)",
                       (user_id, career_goal, roadmap_json_str, checkbox_states_json_str)) # Store empty checkbox_states
        conn.commit()
        print(f"Roadmap for '{career_goal}' stored successfully in SQLite for user: {user_id} with initial checkbox states.")
        return True
    except sqlite3.Error as e:
        print(f"Error storing roadmap in SQLite database: {e}")
        return False


def fetch_roadmap_sqlite(conn, user_id, career_goal):
    """Fetches a specific career roadmap and checkbox states from SQLite database."""
    cursor = conn.cursor()
    cursor.execute("SELECT roadmap_json, checkbox_states FROM career_plans_sqlite WHERE user_id = ? AND career_goal = ?", (user_id, career_goal))
    result = cursor.fetchone()
    if result:
        roadmap_json_str, checkbox_states_str = result # Unpack both roadmap_json and checkbox_states
        roadmap_json = json.loads(roadmap_json_str) # Parse roadmap_json string back to object
        checkbox_states = json.loads(checkbox_states_str) if checkbox_states_str else {} # Parse checkbox_states, default to empty dict if None
        print(f"Roadmap and checkbox states for '{career_goal}' fetched successfully from SQLite for user: {user_id}")
        return roadmap_json, checkbox_states # Return both roadmap_json and checkbox_states
    else:
        print(f"No roadmap found in SQLite for user: {user_id} and career goal: {career_goal}")
        return None, {} # Return None roadmap and empty dict for checkbox_states

def fetch_career_goals_for_user_sqlite(conn, user_id):
    """Fetches a list of career goals for a given user from SQLite database."""
    create_career_plans_table(conn) # Ensure table exists
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT career_goal FROM career_plans_sqlite WHERE user_id = ?", (user_id,))
    results = cursor.fetchall()
    career_goals = [row[0] for row in results] # Extract career goals from tuples
    print(f"Career goals fetched from SQLite for user: {user_id}: {career_goals}")
    return career_goals

def update_checkbox_states_sqlite(conn, user_id, career_goal, checkbox_states):
    """Updates the checkbox states in SQLite database for a specific roadmap."""
    cursor = conn.cursor()
    try:
        checkbox_states_json_str = json.dumps(checkbox_states) # Serialize checkbox_states to JSON string
        cursor.execute("UPDATE career_plans_sqlite SET checkbox_states = ? WHERE user_id = ? AND career_goal = ?",
                       (checkbox_states_json_str, user_id, career_goal))
        conn.commit()
        print(f"Checkbox states updated successfully in SQLite for user: {user_id}, career goal: {career_goal}")
        return True
    except sqlite3.Error as e:
        print(f"Error updating checkbox states in SQLite database: {e}")
        return False
def update_progress_db(user_id, career_goal, checkbox_id): # Removed sqlite_conn from function args, no longer passed as arg
    """Callback function to update checkbox state in SQLite database. Establishes its own DB connection."""
    checkbox_state = st.session_state.get(checkbox_id, False)
    print(f"--- update_progress_db: Checkbox '{checkbox_id}' state changed to: {checkbox_state} ---")

    sqlite_conn = connect_to_sqlite() # Establish NEW SQLite connection WITHIN the callback function
    if sqlite_conn:
        current_checkbox_states = fetch_checkbox_states_from_session_state()
        update_checkbox_states_sqlite(sqlite_conn, user_id, career_goal, current_checkbox_states)
        print(f"--- update_progress_db: Checkbox state updated in database for: {checkbox_id} ---")
        sqlite_conn.close() # Close DB connection AFTER update operation WITHIN the callback
    else:
        print("--- update_progress_db: Warning - Database connection failed. Checkbox state not saved. ---")


if __name__ == "__main__":
    # Example usage (for testing database.py directly)
    conn = connect_to_sqlite()
    if conn:
        test_user_id = "test_user_1"
        test_career_goal = "Persistent Progress Test Goal"
        sample_roadmap = {
            "timeline": {
                "Month 1": {
                    "Fundamentals": ["Learn Python basics (Persistent Progress Test)"]
                }
            }
        }


        # Store roadmap (this will also initialize checkbox_states)
        if store_roadmap_sqlite(conn, test_user_id, test_career_goal, sample_roadmap):
            print("Test roadmap stored successfully in SQLite with initial checkbox states.")

        # Fetch roadmap and checkbox states
        fetched_roadmap, fetched_checkbox_states = fetch_roadmap_sqlite(conn, test_user_id, test_career_goal)
        if fetched_roadmap:
            print("Fetched roadmap from SQLite:")
            print(json.dumps(fetched_roadmap, indent=2))
            print("Fetched checkbox states from SQLite:")
            print(fetched_checkbox_states)
        else:
            print("Failed to fetch roadmap or no roadmap found in SQLite.")

        # Example update checkbox states (for testing)
        updated_checkbox_states = {"Month 1-Fundamentals-Learn Python basics (Persistent Progress Test)": True}
        if update_checkbox_states_sqlite(conn, test_user_id, test_career_goal, updated_checkbox_states):
            print("Checkbox states updated successfully in SQLite.")

        # Fetch roadmap and checkbox states again after update
        fetched_roadmap_updated, fetched_checkbox_states_updated = fetch_roadmap_sqlite(conn, test_user_id, test_career_goal)
        if fetched_roadmap_updated:
            print("Fetched roadmap from SQLite after update:")
            print(json.dumps(fetched_roadmap_updated, indent=2))
            print("Fetched checkbox states from SQLite after update:")
            print(fetched_checkbox_states_updated)
        else:
            print("Failed to fetch roadmap after update.")


        conn.close()