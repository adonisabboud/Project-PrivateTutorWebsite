from server_requests import *
def render_profile_selection():
    """Let the user select their profile type."""
    st.subheader("Select your profile type")
    profile_type = st.radio("Profile Type", ["Student", "Teacher"])

    if st.button("Confirm"):
        st.session_state.profile_type = profile_type
        logging.info(f"User selected profile type: {profile_type}")
        st.experimental_rerun()  # Refresh the page to reflect the profile type in the session state
