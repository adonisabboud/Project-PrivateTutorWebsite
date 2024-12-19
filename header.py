from login_register_logout import *
from select_profile import render_profile_selection
from server_requests import *
def render_authentication_page():
    """Render the login and registration page."""
    st.subheader("Welcome! Please log in or register.")
    auth_action = st.radio("Select Action", ["Login", "Register"])

    email = st.text_input("Email", key="email", placeholder="Enter your email")
    password = st.text_input("Password", key="password", type="password", placeholder="Enter your password")

    # Display registration fields only if 'Register' is selected
    if auth_action == "Register":
        full_name = st.text_input("Full Name", key="full_name", placeholder="Enter your full name")
        username = st.text_input("Username", key="username", placeholder="Enter your username")

    if st.button("Submit"):
        if not email or not password:
            st.warning("Please fill in both email and password.")
            return

        if auth_action == "Login":
            user_profile = login(email, password)
            if user_profile:
                st.session_state.update({
                    "user_id": user_profile.get("id"),
                    "user_authenticated": True
                })
                st.success(f"Welcome back, {user_profile.get('name', 'User')}!")
                if 'profile_type' not in st.session_state or st.session_state.profile_type is None:
                    render_profile_selection()
                return

        elif auth_action == "Register":
            if not full_name or not username:
                st.warning("Please fill out all registration fields.")
                return

            user_profile = register(full_name, username, email, password)
            if user_profile:
                st.session_state.update({
                    "user_id": user_profile.get("id"),
                    "user_authenticated": True
                })
                st.success(f"Welcome, {user_profile.get('name', 'User')}! Please select your profile type.")
                render_profile_selection()
                return

        st.error("Authentication failed. Please try again.")





def toggle_profile():
    """Toggle the profile type between 'Student' and 'Teacher'."""
    new_profile_type = "Teacher" if st.session_state.profile_type == "Student" else "Student"
    st.session_state.profile_type = new_profile_type
    st.experimental_rerun()


def render_header():
    """Render the top bar with the application title and a profile toggle button."""
    # Style for the header
    st.markdown(
        """
        <style>
        .header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f8f9fa;
            padding: 10px 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-radius: 5px;
        }
        .toggle-btn {
            cursor: pointer;
            background-color: #007bff;  /* Default blue, will be overridden by profile type */
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    profile_color = "#007bff" if st.session_state.get('profile_type', 'Student') == "Student" else "#28a745"
    # Adjust button color based on the profile type
    st.markdown(
        f"<style>.toggle-btn {{ background-color: {profile_color}; }}</style>", unsafe_allow_html=True
    )

    # Header content with title and toggle button
    col1, col2 = st.columns([9, 1])
    with col1:
        st.markdown("## Student-Teacher Meeting Scheduler")
    with col2:
        if st.session_state.user_authenticated and 'profile_type' in st.session_state:
            toggle_text = "Switch to Teacher" if st.session_state.profile_type == "Student" else "Switch to Student"
            if st.button(toggle_text, key="profile_toggle"):
                toggle_profile()
