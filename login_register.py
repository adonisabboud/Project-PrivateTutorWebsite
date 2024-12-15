import streamlit as st

import logging

from server_requests import *



def login(email, password):
    """Logs in a user using their email and password."""
    try:
        logger.info("Attempting to log in user.")
        payload = {"email": email, "password": password}
        result = send_data("/users/authenticate", payload)
        logger.debug(f"Login response: {result}")

        if result is None:
            st.error("Login failed due to an API error. Please check the logs.")
            return None

        # Handle the new API response structure
        user_id = result.get("user_id")
        roles = result.get("roles", ["Student"])  # Default to Student if roles are not provided
        message = result.get("message", "Login successful.")

        if user_id:
            # Update session state for the logged-in user
            st.session_state.user_id = user_id
            st.session_state.profile_type = roles[0]  # Assume the first role is the primary role
            st.session_state.user_authenticated = True
            logger.info(f"Login successful for user {email}")
            st.success(message)
            return result
        else:
            logger.error(f"Login failed: {result}")
            st.error("Invalid email or password. Please try again.")
            return None
    except Exception as e:
        logger.exception(f"Login failed for user {email}: {e}")
        st.error("An unexpected error occurred during login. Please try again.")
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
        logger.debug(f"Registration response: {result}")

        if result is None:
            st.error("Registration failed due to an API error. Please check the logs.")
            return None

        # Handle the new API response structure
        user_id = result.get("user_id")
        message = result.get("message", "Registration successful.")

        if user_id:
            logger.info(f"User registered successfully: {email}")
            st.success(message)

            # Automatically log in the user
            st.session_state.user_id = user_id
            st.session_state.profile_type = profile_type
            st.session_state.user_authenticated = True
            return True  # Indicate success
        else:
            logger.error(f"Registration failed: {result}")
            st.error(f"Registration failed: {result}")
            return None
    except Exception as e:
        logger.exception(f"Registration failed: {e}")
        st.error("An unexpected error occurred during registration. Please try again.")
        return None


def logout():
    """Logs out the user by clearing session state."""
    logger.info(f"Logging out user {st.session_state.get('user_id')}")
    st.session_state.clear()
    st.success("You have been logged out.")

