import streamlit as st

import logging

from server_requests import send_data

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def login(email, password):
    """Logs in a user using their email and password."""
    try:
        logger.info("Attempting to log in user.")
        payload = {"email": email, "password": password}
        user_profile = send_data("/users/authenticate", payload)
        if user_profile and "id" in user_profile:
            st.session_state.user_id = user_profile["id"]
            st.session_state.profile_type = user_profile.get("roles", ["Student"])[0]
            st.session_state.user_authenticated = True
            logger.info(f"Login successful for user {email}")
            return user_profile
        else:
            logger.error("Login failed. Invalid email or password.")
            st.error("Invalid email or password.")
            return None
    except Exception as e:
        logger.exception(f"Login failed for user {email}: {e}")
        st.error("An unexpected error occurred. Please try again.")
        return None

def register(name, username, email, password, profile_type):
    """Registers a new user and logs them in automatically."""
    try:
        logger.info("Registering new user.")
        payload = {
            "name": name,
            "username": username,
            "email": email,
            "password": password,
            "roles": [profile_type],
        }
        result = send_data("/users", payload)
        if result and "id" in result:
            st.session_state.user_id = result["id"]
            st.session_state.profile_type = profile_type
            st.session_state.user_authenticated = True
            logger.info(f"User registered successfully: {email}")
            return login(email, password)
        else:
            logger.error("Registration failed.")
            st.error("Registration failed. Please try again.")
            return None
    except Exception as e:
        logger.exception(f"Registration failed: {e}")
        st.error("An unexpected error occurred. Please try again.")
        return None


def logout():
    """Logs out the user by clearing session state."""
    logger.info(f"Logging out user {st.session_state.get('user_id')}")
    st.session_state.clear()
    st.success("You have been logged out.")

