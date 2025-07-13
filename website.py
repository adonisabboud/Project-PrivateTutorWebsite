from login_register_logout import *
from server_requests import *
from student_view import student_view
from teacher_view import teacher_view
import streamlit as st
from datetime import datetime
import time


def main():
    # Initialize session state variables
    if "user_id" not in st.session_state:
        st.session_state.update({
            "user_id": None,
            "user_authenticated": False,
            "profile_type": None,
            "navigation": "auth",  # Controls navigation state
        })

    # Render header
    render_header()

    # Handle navigation dynamically
    if st.session_state.navigation == "auth":
        render_authentication_page()
    elif st.session_state.navigation == "profile_creation":
        render_profile_creation()
    elif st.session_state.navigation == "main_app":
        render_main_app()


def render_header():
    """Render the application header with toggle and logout button."""
    st.title("Welcome to the Scheduler")
    if st.session_state.user_authenticated:
        col1, col2 = st.columns([6, 1])  # Adjust layout for toggle and logout button
        with col1:
            if st.session_state.profile_type:
                toggle_text = (
                    "Switch to Teacher" if st.session_state.profile_type == "Student" else "Switch to Student"
                )
                if st.button(toggle_text):
                    toggle_profile()
        with col2:
            if st.button("Logout"):
                logout()


def toggle_profile():
    """Toggle between student and teacher profiles, and create one if it doesn't exist."""
    new_profile_type = "Teacher" if st.session_state.profile_type == "Student" else "Student"

    # Check if the new profile exists
    if not check_existing_profile(new_profile_type):
        create_profile(new_profile_type)

    # Switch the profile
    st.session_state.profile_type = new_profile_type
    st.success(f"Switched to {new_profile_type} profile!")


def validate_and_convert_intervals(intervals):
    """Ensure all time intervals are dictionaries with ISO 8601 'start' and 'end' strings."""
    validated = []

    for item in intervals:
        if not isinstance(item, dict):
            continue  # skip if not a dictionary

        start = item.get("start")
        end = item.get("end")

        if isinstance(start, datetime) and isinstance(end, datetime):
            validated.append({
                "start": start.isoformat(),
                "end": end.isoformat()
            })
        elif isinstance(start, str) and isinstance(end, str):
            try:
                # Make sure the strings are valid ISO datetime strings
                datetime.fromisoformat(start)
                datetime.fromisoformat(end)
                validated.append({
                    "start": start,
                    "end": end
                })
            except ValueError:
                continue  # skip invalid string formats
        # else: skip silently if data is malformed
    return validated


def create_profile(profile_type):
    """Automatically create a profile if it doesn't exist."""
    user_id = st.session_state.user_id
    user_name = st.session_state.get("user_name", "Unknown User")
    user_email = st.session_state.get("user_email", "")
    phone = st.session_state.get("phone", "Unknown")
    about = st.session_state.get("about_section", "Default profile")

    raw_intervals = st.session_state.get("available_intervals", [])
    available_intervals = validate_and_convert_intervals(raw_intervals)

    if profile_type == "Student":
        payload = {
            "id": user_id,
            "name": user_name,
            "phone": phone,
            "email": user_email,
            "about_section": about,
            "available": available_intervals,
            "rating": 0,
            "subjects_interested_in_learning": st.session_state.get("subjects", ["General"]),
            "meetings": [],
        }

        # st.subheader("📦 Student Payload Debug")
        # st.json(payload)

        response = send_data("/students", data=payload)
        if response:
            st.success("Student profile created!")
        else:
            st.error("Failed to create student profile.")

    elif profile_type == "Teacher":
        payload = {
            "id": user_id,
            "name": user_name,
            "phone": phone,
            "email": user_email,
            "about_section": about,
            "available": available_intervals,
            "rating": 0,
            "subjects_to_teach": st.session_state.get("subjects", ["General"]),
            "hourly_rate": st.session_state.get("rate", 10),
            "meetings": [],
        }

        # st.subheader("📦 Teacher Payload Debug")
        # st.json(payload)

        response = send_data("/teachers", data=payload)
        if response:
            st.success("Teacher profile created!")
        else:
            st.error("Failed to create teacher profile.")


def render_authentication_page():
    """Render the login and registration interface."""

    if st.session_state.get("temp_login_success"):
        st.session_state.navigation = "profile_creation"
        st.session_state.temp_login_success = False
        st.rerun()  # Skip rendering below

    if not st.session_state.get("user_authenticated", False):
        auth_action = st.radio("Login or Register", ["Login", "Register"], key="auth_action")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        full_name = st.text_input("Full Name",
                                  placeholder="Enter your full name") if auth_action == "Register" else None
        username = st.text_input("Username", placeholder="Choose a username") if auth_action == "Register" else None

        if st.button("Submit"):
            handle_auth(auth_action, email, password, full_name, username)
    else:
        st.success(f"Welcome back, {st.session_state.get('user_name', 'User')}!")


def handle_auth(auth_action, email, password, full_name=None, username=None):
    """Handle authentication for login or registration."""
    if not email or not password:
        st.warning("Please fill in both email and password.")
        return

    if auth_action == "Login":
        user_profile = login(email, password)
        if user_profile:
            update_session(user_profile)
            st.session_state.temp_login_success = True
            st.rerun()
        else:
            st.error("Login failed. Please try again.")

    elif auth_action == "Register":
        if not full_name or not username:
            st.warning("Please complete all registration fields.")
            return

        user_profile = register(full_name, username, email, password)
        if user_profile:
            update_session(user_profile)
            st.session_state.temp_login_success = True
            st.rerun()
        else:
            st.error("Registration failed. Please try again.")


def update_session(user_profile):
    """Update session state with user information."""
    str_id = user_profile.get("user_id")
    st.session_state.user_id = str(str_id)
    print(f"printing str_id :-> {str_id}")  # Outputs the string ID

    # get user by id by calling the endpoint Request URL
    # https://project-privatetutor.onrender.com/users/id/676823f1e3603040e08723a3
    # now we update the fields
    st.session_state.user_authenticated = True
    st.session_state.profile_type = None  # Reset profile type
    # Store additional information
    user_data = get_user_data(st.session_state.user_id)
    st.session_state.user_name = user_profile.get("name", "User")
    st.session_state.user_email = user_data.get("email", "")


###################################################

def display_profile(profile):
    """Display user profile details in a readable format."""
    st.subheader("Profile Details")
    st.write(f"**Name:** {profile['name']}")
    st.write(f"**Email:** {profile['email']}")
    if profile.get('phone'):
        st.write(f"**Phone:** {profile['phone']}")
    if profile.get('about_section'):
        st.write(f"**About:** {profile['about_section']}")
    if profile.get('available_intervals'):
        st.write("**Available Intervals:**")
        for interval in profile['available_intervals']:
            st.write(f"From {interval['start']} to {interval['end']}")


def render_profile_creation():
    """Improved version: handles welcome spinner and role-based profile creation."""
    with st.spinner(f"Welcome back, {st.session_state.get('user_name', 'User')}! Loading your profile..."):
        time.sleep(2)

    st.title("Create Your Profile")
    profile_type = st.radio("Select Your Role", ["Student", "Teacher"], key="profile_type_selection")

    # Check if the profile already exists
    existing_profile = check_existing_profile(profile_type)
    if existing_profile:
        display_profile(existing_profile)
        if st.button("Continue"):
            st.session_state.profile_type = profile_type
            st.session_state.navigation = "main_app"
            st.success("Proceeding to the next step...")
        #st.json(existing_profile)
        return

    # Inputs
    phone = st.text_input("Phone", placeholder="Enter your phone number")
    about_section = st.text_area("About You", placeholder="Write something about yourself")

    st.markdown("### 📅 Available Time Intervals")
    start_date = st.date_input("Select Start Date", key="start_date")
    start_time = st.time_input("Select Start Time", key="start_time")
    end_date = st.date_input("Select End Date", key="end_date")
    end_time = st.time_input("Select End Time", key="end_time")
    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)

    if "available_intervals" not in st.session_state:
        st.session_state.available_intervals = []

    if st.button("➕ Add Time Interval"):
        if end_dt <= start_dt:
            st.error("End time must be after start time.")
        else:
            st.session_state.available_intervals.append({
                "start": start_dt,
                "end": end_dt
            })
            st.success("Time interval added!")

    st.markdown("#### 🕒 Current Available Time Intervals:")
    for i, interval in enumerate(st.session_state.available_intervals):
        st.write(f"{i + 1}. {interval['start']} to {interval['end']}")
        if st.button(f"Delete {i}", key=f"delete_{i}"):
            st.session_state.available_intervals.pop(i)
            st.rerun()

    id = st.session_state.get("user_id")
    name = st.session_state.get("user_name")
    email = st.session_state.get("user_email")

    if profile_type == "Student":
        subjects = st.text_area("Subjects You Want to Learn", placeholder="E.g., Math, Physics")
        if st.button("Create Student Profile"):
            create_student_profile(
                id=id,
                name=name,
                phone=phone,
                email=email,
                about_section=about_section,
                subjects_interested_in_learning=[s.strip() for s in subjects.split(",")],
                available_intervals=st.session_state.available_intervals
            )

    elif profile_type == "Teacher":
        subjects = st.text_area("Subjects You Can Teach", placeholder="E.g., Math, Physics")
        hourly_rate = st.number_input("Hourly Rate", min_value=0, step=1)
        if st.button("Create Teacher Profile"):
            create_teacher_profile(
                id=id,
                name=name,
                phone=phone,
                email=email,
                about_section=about_section,
                subjects_to_teach=[s.strip() for s in subjects.split(",")],
                hourly_rate=hourly_rate,
                available_intervals=st.session_state.available_intervals
            )


def create_student_profile(id, name, phone, email, about_section, subjects_interested_in_learning, available_intervals):
    """Send a request to create a student profile."""

    # ✅ Validate intervals
    validated_intervals = validate_and_convert_intervals(available_intervals)

    payload = {
        "id": id,
        "name": name,
        "phone": phone,
        "email": email,
        "about_section": about_section,
        "available": validated_intervals,
        "rating": 0,
        "subjects_interested_in_learning": subjects_interested_in_learning,
        "meetings": [],
    }

    response = send_data("/students", data=payload)
    if response:
        st.session_state.profile_type = "Student"
        st.session_state.navigation = "main_app"
        st.success("Student profile created successfully!")
    else:
        st.error("Failed to create student profile. Please try again.")


def create_teacher_profile(id, name, phone, email, about_section, subjects_to_teach, hourly_rate, available_intervals):
    validated_intervals = validate_and_convert_intervals(available_intervals)
    payload = {
        "id": id,
        "name": name,
        "phone": phone,
        "email": email,
        "about_section": about_section,
        "available": validated_intervals,
        "rating": 0,
        "subjects_to_teach": subjects_to_teach,
        "hourly_rate": hourly_rate,
        "meetings": [],
    }
    response = send_data("/teachers", data=payload)
    if response:
        st.session_state.profile_type = "Teacher"
        st.session_state.navigation = "main_app"
        st.success("Teacher profile created successfully!")
    else:
        st.error("Failed to create teacher profile. Please try again.")


def render_main_app():
    """Render the main application interface."""
    st.title(f"Welcome to the {st.session_state.profile_type} Dashboard")

    if st.session_state.profile_type == "Student":
        student_view()
    elif st.session_state.profile_type == "Teacher":
        teacher_view()

    # st.header("Your Meetings")
    # user_id = st.session_state.get("user_id")
    # if not user_id:
    #     st.error("No user ID found. Please log in again.")
    #     return
    #
    # meetings = fetch_user_meetings(user_id)
    #
    # if meetings:
    #     for meeting in meetings:
    #         st.write(f"**Subject**: {meeting['subject']}")
    #         st.write(f"**Location**: {meeting['location']}")
    #         st.write(f"**Start Time**: {meeting['start_time']}")
    #         st.write(f"**Finish Time**: {meeting['finish_time']}")
    #         st.write(f"**Participants**: {', '.join(meeting['people'])}")
    #         st.markdown("---")
    # else:
    #     st.info("You have no scheduled meetings.")


if __name__ == "__main__":
    main()
