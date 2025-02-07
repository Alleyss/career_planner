import streamlit as st
from components.home import home_page
from components.dashboard import dashboard_page
from components.auth import auth_page # Import auth_page

def main():
    st.sidebar.title("Navigation")

    if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']: # Check authentication status
        page = "Authentication" # Default to auth page if not logged in
    else:
        page_options = ["Generate Plan", "Monitor Goal", "Logout"] # Add Logout to options
        page = st.sidebar.radio("Go to", page_options) # Radio buttons for navigation

        if page == "Logout": # Handle Logout
            st.session_state['authentication_status'] = False # Clear auth status
            st.session_state['name'] = None # Clear username
            st.rerun() # Rerun to update UI and redirect to auth page
            return # Exit main function after logout

    if page == "Generate Plan":
        home_page()
    elif page == "Monitor Goal":
        dashboard_page()
    elif page == "Authentication": # Authentication Page
        auth_page()

if __name__ == "__main__":
    main()