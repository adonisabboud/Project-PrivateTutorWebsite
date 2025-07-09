from server_requests import *


def login(email, password):
    """
    Handle user login and return user profile on success.

    Args:
        email (str): User's email.
        password (str): User's password.

    Returns:
        dict or None: The server's response (parsed JSON) on success; None on failure.
    """
    logger.info("Attempting to log in user.")
    try:
        payload = {"email": email, "password": password}
        result = send_data("/users/login", data=payload, method="POST")
        st.write("Login response:", result)  # 🔍 Debug output

        if result and "user_id" in result:
            logger.info(f"Login successful for user {email}")
            st.session_state.user_id = result["user_id"]
            return result
        elif result and "detail" in result:
            logger.error(f"Login failed: {result['detail']}")
            st.error(result["detail"])
            return None
        else:
            logger.error("Login failed: Unknown error.")
            st.error("Login failed. Please try again.")
            return None
    except Exception as e:
        logger.exception(f"Login failed due to an unexpected error: {e}")
        st.error("An unexpected error occurred. Please try again later.")
        return None


def register(name, username, email, password):
    """Handle user registration and return user details."""
    try:
        logger.info("Registering new user.")
        payload = {"name": name, "username": username, "email": email, "password": password, "roles": []}
        result = send_data("/users", payload)
        st.write("Registration response:", result)  # 🔍 Debug output

        if result and "user_id" in result:
            logger.info("Registration successful.")
            return result
        else:
            logger.error("Registration failed.")
            return None
    except Exception as e:
        logger.exception("Registration failed.")
        return None


def logout():
    """Log out the user by clearing session state and resetting authentication state."""
    logger.info("Logging out user.")
    st.session_state.clear()
    st.session_state.update({
        "user_id": None,
        "user_authenticated": False,
        "profile_type": None,
        "navigation": "auth"
    })
    st.success("You have been logged out.")
