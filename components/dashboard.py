import streamlit as st
from backend.database import connect_to_sqlite, fetch_roadmap_sqlite, fetch_career_goals_for_user_sqlite, update_checkbox_states_sqlite  # Updated imports
from components.roadmap_display import display_roadmap_with_checkboxes # Import display_roadmap_with_checkboxes

def dashboard_page():
    if 'name' not in st.session_state:
        st.error("Please Login to Monitor Your Goal")
        return

    st.title("Goal Monitoring Dashboard")
    st.write("Track your progress and stay motivated on your career path!")

    sqlite_conn = connect_to_sqlite()
    if sqlite_conn:
        user_id = st.session_state['name']
        career_goals = fetch_career_goals_for_user_sqlite(sqlite_conn, user_id)
        selected_career_goal = None

        if career_goals:
            if not career_goals:
                st.info(f"No career plans generated yet for user: {user_id}.")
                return

            selected_career_goal = st.selectbox("Select Career Goal to Monitor:", career_goals)

            if selected_career_goal:
                print(f"\n--- Dashboard: Fetching roadmap for user: {user_id}, Career Goal: {selected_career_goal} (SQLite) ---")
                roadmap_json, checkbox_states = fetch_roadmap_sqlite(sqlite_conn, user_id, selected_career_goal) # Fetch roadmap AND checkbox_states

                if roadmap_json:
                    st.success(f"Roadmap retrieved for user: {user_id}, Goal: {selected_career_goal}")
                    st.subheader(f"Your Career Roadmap: {selected_career_goal}")
                    display_roadmap_with_checkboxes(roadmap_json, checkbox_states, user_id, selected_career_goal) # Call display_roadmap_with_checkboxes with states and db info
                else:
                    st.info(f"No roadmap found for user: {user_id} with goal: {selected_career_goal}.")
            else:
                st.info("Please select a career goal to view the roadmap.")
        else:
            st.error("Failed to fetch career goals for user. No career plans found in SQLite database.")
        sqlite_conn.close()


        # Placeholder for roadmap checklist and progress tracking (we'll add this in Phase 4)
        st.subheader("Your Roadmap Progress (Persistent):") # Updated subheader
        st.write("Roadmap checklist and progress visualization are implemented above (progress is now saved in SQLite database).")

    else:
        st.error("Database connection failed on dashboard. Cannot display roadmap.")
        st.error("Check console for SQLite connection errors.")


if __name__ == "__main__":
    dashboard_page()