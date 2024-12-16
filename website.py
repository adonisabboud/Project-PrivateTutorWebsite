

from login_register import login, register
from server_requests import *  # Assuming this imports the necessary backend functions
from teacher_student_view import *

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    # Initialize session state variables
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
        st.session_state.profile_type = "Student"  # Default profile type
        st.session_state.user_authenticated = False  # Whether the user is logged in or not

    # Render header and profile toggle bar
    render_header()

    # Show login/register screen if the user is not authenticated
    if not st.session_state.user_authenticated:
        render_authentication_page()
    else:
        # Render the main app based on the selected profile type
        if st.session_state.profile_type == "Student":
            student_view()
        elif st.session_state.profile_type == "Teacher":
            teacher_view()


def render_header():
    """Render the top bar with the profile toggle."""
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
        }
        .toggle-btn {
            cursor: pointer;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([9, 1])  # Split screen: 90% width for title, 10% for toggle
    with col1:
        st.title("Student-Teacher Meeting Scheduleer")
    with col2:
        if st.session_state.user_authenticated:
            if st.button(f"{st.session_state.profile_type}"):
                toggle_profile()

def render_header():
    """Render the top bar with the profile toggle."""
    profile_color = "#007bff" if st.session_state.profile_type == "Student" else "#28a745"
    st.markdown(
        f"""
        <style>
        .header-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: {profile_color};
            padding: 10px 20px;
            color: white;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
        }}
        .toggle-btn {{
            cursor: pointer;
            background-color: white;
            color: {profile_color};
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        }}
        </style>
        <div class="header-bar">
            <div>Student-Teacher Meeting Scheduler</div>
            <button class="toggle-btn" onclick="window.location.reload()">{st.session_state.profile_type}</button>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_authentication_page():
    """Render the login and registration page."""
    st.subheader("Welcome! Please log in or register.")
    auth_action = st.radio("Select Action", ["Login", "Register"], key="auth_action")

    if auth_action == "Login":
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login"):
            if not email or not password:
                st.warning("Please fill in both email and password.")
            else:
                user_profile = login(email, password)
                if user_profile:
                    st.session_state.user_id = user_profile.get("id")
                    st.session_state.profile_type = user_profile.get("roles", ["Student"])[0]
                    st.session_state.user_authenticated = True
                    st.success(f"Welcome back, {user_profile.get('name', 'User')}!")
                else:
                    st.error("Invalid email or password. Please try again.")

    elif auth_action == "Register":
        full_name = st.text_input("Full Name", placeholder="Enter your full name")
        username = st.text_input("Username", placeholder="Enter your username")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        profile_type = st.radio("Profile Type", ["Student", "Teacher"], key="profile_type")

        if st.button("Register"):
            if not full_name or not username or not email or not password:
                st.warning("All fields are required for registration. Please fill out all fields.")
            else:
                user_profile = register(full_name, username, email, password, profile_type)
                if user_profile:
                    st.session_state.user_id = user_profile.get("id")
                    st.session_state.profile_type = user_profile.get("roles", ["Student"])[0]
                    st.session_state.user_authenticated = True
                    st.success(f"Welcome, {user_profile.get('name', 'User')}! You are now logged in.")
                else:
                    st.error("Registration failed. Please try again.")


def toggle_profile():
    """Toggle between Student and Teacher profiles."""
    st.session_state.profile_type = "Teacher" if st.session_state.profile_type == "Student" else "Student"
    logging.info(f"Profile type switched to {st.session_state.profile_type}")
    st.experimental_rerun()  # Rerun the app to reflect the change


if __name__ == "__main__":
    main()
