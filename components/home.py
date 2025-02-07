import streamlit as st
from backend.ai_agent import generate_career_roadmap
from backend.database import connect_to_sqlite, store_roadmap_sqlite # Updated imports

def home_page():
    if 'name' not in st.session_state: # Check if username is in session state
        st.error("Please Login to Generate Career Plan") # Show error and halt if not logged in
        return

    st.title("Career Planner AI")
    st.write("Tell us about your background and career goals to generate a personalized roadmap.")

    with st.form("user_input_form"):
        education_status = st.selectbox(
            "Education Status",
            ["High School", "Some College", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "Doctorate", "Other"]
        )
        career_goal = st.text_input("Career Goal (e.g., AI Engineer, Data Scientist, Web Developer)")
        resources_available = st.text_area("Resources Available (e.g., time per week, budget for courses, existing skills)")
        timeline = st.selectbox(
            "Timeline (in months)",
            [i for i in range(1, 25)] # Options from 1 to 24 months
        )

        generate_plan_button = st.form_submit_button("Generate Career Plan")

    if generate_plan_button:
        with st.spinner("Generating your personalized career roadmap..."):
            roadmap_json = generate_career_roadmap(education_status, career_goal, resources_available, timeline)

        if roadmap_json:
            st.success("Career roadmap generated successfully!")

            # --- SQLite Database Integration ---
            sqlite_conn = connect_to_sqlite() # Connect to SQLite
            if sqlite_conn:
                user_id = st.session_state['name']  # Use username from session state as user_id
                if store_roadmap_sqlite(sqlite_conn, user_id, career_goal, roadmap_json): # Store in SQLite
                    st.success("Roadmap saved to database for tracking!")
                else:
                    st.error("Failed to save roadmap to database. Check console for database errors.")
                sqlite_conn.close() # Close SQLite connection
            else:
                st.error("Database connection failed. Roadmap not saved.")
                st.error("Check console for SQLite connection errors.")


            # --- Display Roadmap with Expanders ---
            st.subheader("Your Career Roadmap:")
            if "timeline" in roadmap_json and roadmap_json["timeline"]: # Check if timeline data exists
                timeline_data = roadmap_json["timeline"]
                for duration, duration_content in timeline_data.items(): # Iterate through months/durations
                    with st.expander(f"**{duration}**", expanded=False): # Expander for each duration
                        for topic, sub_topics in duration_content.items(): # Iterate through topics within duration
                            if topic != "Resources": # Handle Resources separately
                                st.markdown(f"**{topic}:**") # Topic as bold text
                                if isinstance(sub_topics, list): # Check if sub_topics is a list
                                    for sub_topic in sub_topics:
                                        st.markdown(f"- {sub_topic}") # Sub-topics as bullet points
                                elif isinstance(sub_topics, dict): # Handle nested topics if structure changes
                                    for sub_topic_group, sub_topic_list in sub_topics.items():
                                        st.markdown(f"  - **{sub_topic_group}:**") # Sub-topic group (if needed)
                                        for sub_item in sub_topic_list:
                                            st.markdown(f"- {sub_item}") # Sub-items
                            elif topic == "Resources": # Display Resources
                                if isinstance(sub_topics, list):
                                    st.markdown("**Resources:**")
                                    for resource in sub_topics:
                                        st.markdown(f"- {resource}")
                                elif isinstance(sub_topics, dict): # Handle resources as dict if needed
                                    st.markdown("**Resources:**")
                                    for resource_type, resource_list in sub_topics.items():
                                        st.markdown(f"  - **{resource_type}:**")
                                        for resource_item in resource_list:
                                            st.markdown(f"- {resource_item}")
            else:
                st.warning("No roadmap timeline data found in the generated plan.") # Message if timeline is missing


        else:
            st.error("Failed to generate career roadmap. Please check the console for errors.")

if __name__ == "__main__":
    home_page()