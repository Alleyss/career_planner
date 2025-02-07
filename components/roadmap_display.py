import streamlit as st
from backend.database import update_checkbox_states_sqlite, connect_to_sqlite  # Import connect_to_sqlite

def display_roadmap_with_checkboxes(roadmap_json, checkbox_states, user_id, career_goal):
    """
    Parses and displays the career roadmap JSON with checkboxes for progress tracking, persisting state in SQLite.

    Args:
        roadmap_json (dict): The JSON-like dictionary representing the career roadmap.
        checkbox_states (dict): Dictionary of checkbox states loaded from database.
        user_id (str): User identifier.
        career_goal (str): Career goal for the roadmap.
    """
    st.subheader("Your Career Roadmap:")
    if "timeline" in roadmap_json and roadmap_json["timeline"]:
        timeline_data = roadmap_json["timeline"]
        total_sub_topics = 0
        completed_sub_topics = 0

        # Initialize checkbox states from fetched checkbox_states dictionary
        # st.session_state['checkbox_states'] = checkbox_states # No longer needed to initialize here, passed directly

        for duration, duration_content in timeline_data.items():
            with st.expander(f"**{duration}**", expanded=False):
                for topic, sub_topics in duration_content.items():
                    if isinstance(sub_topics, list):
                        st.markdown(f"**{topic}:**")
                        for sub_topic in sub_topics:
                            total_sub_topics += 1
                            checkbox_id = f"{duration}-{topic}-{sub_topic}-checkbox" # More specific checkbox_id
                            # Use fetched checkbox_states to initialize checkbox value
                            checked = st.checkbox(sub_topic, key=checkbox_id, value=checkbox_states.get(checkbox_id, False), on_change=update_progress_db, args=(user_id, career_goal, checkbox_id)) # Pass update function and args
                            # No longer updating session state directly here - update happens in update_progress_db callback
                            if checked:
                                completed_sub_topics += 1
                    elif isinstance(sub_topics, dict):
                        st.markdown(f"**{topic}:**")
                        for sub_topic_group, sub_topic_list in sub_topics.items():
                            st.markdown(f"  - **{sub_topic_group}:**")
                            for sub_item in sub_topic_list:
                                total_sub_topics += 1
                                checkbox_id = f"{duration}-{topic}-{sub_topic_group}-{sub_item}-checkbox" # More specific checkbox_id
                                checked = st.checkbox(sub_item, key=checkbox_id, value=checkbox_states.get(checkbox_id, False), on_change=update_progress_db,  args=(user_id, career_goal, checkbox_id)) # Pass update function and args
                                if checked:
                                    completed_sub_topics += 1
                    elif topic == "Resources":
                        if isinstance(sub_topics, list):
                            st.markdown("**Resources:**")
                            for resource in sub_topics:
                                st.markdown(f"- {resource}")
                        elif isinstance(sub_topics, dict):
                            st.markdown("**Resources:**")
                            for resource_type, resource_list in sub_topics.items():
                                st.markdown(f"  - **{resource_type}:**")
                                for resource_item in resource_list:
                                    st.markdown(f"    - {resource_item}")

        if total_sub_topics > 0:
            progress_percentage = (completed_sub_topics / total_sub_topics)
            st.subheader(f"Progress: {completed_sub_topics}/{total_sub_topics} Sub-topics Completed ({progress_percentage*100:.2f}%)")
            st.progress(progress_percentage)
        else:
            st.info("No trackable sub-topics found in the roadmap.")
    else:
        st.warning("No roadmap timeline data found in the generated plan.")


def update_progress_db(user_id, career_goal, checkbox_id):
    """Callback function to update checkbox state in SQLite database. Establishes its own DB connection."""
    checkbox_state = st.session_state.get(checkbox_id, False)
    print(f"--- update_progress_db: Checkbox '{checkbox_id}' state changed to: {checkbox_state} ---")

    sqlite_conn = connect_to_sqlite() # Establish NEW SQLite connection WITHIN the callback function
    if sqlite_conn:
        current_checkbox_states = fetch_checkbox_states_from_session_state() # Get all checkbox states from session state
        update_checkbox_states_sqlite(sqlite_conn, user_id, career_goal, current_checkbox_states) # Update DB with all states
        print(f"--- update_progress_db: Checkbox state updated in database for: {checkbox_id} ---")
        sqlite_conn.close() # Close DB connection after update
    else:
        print("--- update_progress_db: Warning - Database connection failed. Checkbox state not saved. ---")

def fetch_checkbox_states_from_session_state():
    """Helper function to fetch all checkbox states from session state."""
    checkbox_states = {}
    for key, value in st.session_state.items():
        if key.endswith("-checkbox"): # Identify checkbox keys (more robust by checking for suffix)
            checkbox_states[key] = value
    return checkbox_states


if __name__ == "__main__":
    # Example usage (for testing roadmap_display.py directly - you might need to create a sample roadmap_json)
    st.title("Roadmap Display Component Test")
    sample_roadmap_json = {
      "timeline": {
        "Month 1-2": {
          "Fundamentals": ["Python Basics", "Linear Algebra"],
          "Resources": ["Resource 1", "Resource 2"]
        },
        "Month 3-4": {
          "Machine Learning": ["Supervised Learning", "Unsupervised Learning"],
          "Resources": ["Resource 3", "Resource 4"]
        }
      }
    }
    st.write("Sample Roadmap JSON:")
    st.json(sample_roadmap_json)
    st.session_state['checkbox_states'] = {} # Initialize session state for testing
    display_roadmap_with_checkboxes(sample_roadmap_json, st.session_state['checkbox_states'], "test_user", "Test Goal") # Pass empty checkbox_states for initial test