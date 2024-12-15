import streamlit as st
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Helper Methods
def handle_response(response, success_message=None):
    """
    Handle the API response and return parsed data or None.

    Args:
        response (requests.Response): The API response object.
        success_message (str, optional): Message to show on success.

    Returns:
        dict or list: The parsed JSON response if successful; None otherwise.
    """
    if response.status_code in [200, 201]:
        if success_message:
            st.success(success_message)
        return response.json()
    else:
        error_message = response.json().get("detail", "An error occurred.")
        logger.error(f"API Error: {response.status_code} - {response.text}")
        st.error(f"Error: {error_message}")
        return None


# API Interactions
def fetch_data(endpoint, params=None):
    """Fetch data from an endpoint with optional query parameters."""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
        logger.info(f"Fetching data from endpoint: {endpoint}")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params)
        return handle_response(response)
    except Exception as e:
        logger.exception(f"Exception occurred while fetching data from {endpoint}: {e}")
        st.error("An unexpected error occurred while fetching data.")
        return []


def send_data(endpoint, data, method="POST"):
    """Send data to an endpoint with method flexibility."""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
        logger.info(f"Sending data to endpoint: {endpoint} using {method}")
        url = f"{BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=headers, json=data)
        return handle_response(response)
    except Exception as e:
        logger.exception(f"Exception occurred while sending data to {endpoint}: {e}")
        st.error("An unexpected error occurred while sending data.")
        return None


def get_my_meetings(user_id):
    """
    Fetches all meetings and filters them by the user's ID.

    Args:
        user_id (str): The logged-in user's ID.

    Returns:
        list: List of meetings involving the user.
    """
    try:
        logger.info(f"Fetching meetings for user {user_id}")
        my_meetings = fetch_data(f"/meetings/user/{user_id}")
        if not my_meetings:
            logger.info("No meetings found for the user.")
        return my_meetings or []
    except Exception as e:
        logger.exception(f"Error fetching meetings for user {user_id}: {e}")
        return []

# Meeting Management
def request_meeting_with_teacher(teacher_id):
    """
    Allows a student to request a meeting with a teacher.

    Args:
        teacher_id (str): The ID of the teacher to meet with.
    """
    try:
        logger.info(f"Requesting a meeting with teacher {teacher_id}")
        teacher = fetch_data(f"/teachers/{teacher_id}")
        if not teacher:
            st.error("Teacher not found.")
            logger.error(f"Teacher not found: {teacher_id}")
            return

        st.write(f"Requesting a meeting with {teacher.get('name', 'N/A')}")
        available_times = teacher.get('available_times', [])
        if not available_times:
            st.info(f"No available times for {teacher.get('name', 'N/A')}")
            return

        selected_time = st.selectbox("Select an available time", available_times)
        meeting_subject = st.text_input("Meeting Subject", help="Enter the subject of the meeting.")
        meeting_location = st.text_input("Meeting Location", help="Enter the meeting location.")

        if st.button("Request Meeting"):
            if not meeting_subject or not meeting_location:
                st.warning("Please provide both subject and location for the meeting.")
                return

            meeting_data = {
                "teacher_id": teacher_id,
                "student_id": st.session_state.get("user_id"),
                "start_time": selected_time,
                "subject": meeting_subject,
                "location": meeting_location,
            }
            if send_data("/meetings", meeting_data):
                logger.info(f"Meeting request sent: {meeting_data}")
                st.success("Meeting successfully requested!")
            else:
                st.error("Failed to request the meeting. Please try again.")
    except Exception as e:
        logger.exception(f"Error requesting meeting with teacher {teacher_id}: {e}")
        st.error("An unexpected error occurred. Please try again.")

def send_data(endpoint, data=None, method="POST"):
    """
    Send data to a specified API endpoint using the desired HTTP method.

    Args:
        endpoint (str): The API endpoint to send the data to.
        data (dict, optional): The payload to send to the server.
        method (str): The HTTP method to use (e.g., "POST", "PUT", "DELETE").

    Returns:
        dict or None: The server's response (parsed JSON) on success; None on failure.
    """
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.get('token', '')}",
            "Content-Type": "application/json"
        }
        url = f"{BASE_URL}{endpoint}"
        logger.info(f"Sending {method} request to {url} with data: {data}")

        if method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, json=data)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            st.error(f"Unsupported HTTP method: {method}")
            return None

        # Handle response
        return handle_response(response)
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request to {endpoint} failed: {e}")
        st.error("A network error occurred. Please check your connection and try again.")
        return None


def get_my_meetings(user_id):
    try:
        logger.info(f"Fetching meetings for user ID: {user_id}")
        if not user_id:
            logger.error("User ID is None. Cannot fetch meetings.")
            st.error("Please log in to view your meetings.")
            return []

        endpoint = f"/meetings/user/{user_id}"
        meetings = fetch_data(endpoint)
        if meetings:
            logger.info(f"Retrieved {len(meetings)} meetings for user {user_id}")
            return meetings
        else:
            logger.info(f"No meetings found for user {user_id}")
            return []
    except Exception as e:
        logger.exception(f"Error fetching meetings for user {user_id}: {e}")
        st.error("Failed to load meetings. Please try again later.")
        return []


def update_profile(about_section):
    """Updates the user's profile."""
    user_id = st.session_state.get("user_id")
    if not user_id:
        logger.error("Cannot update profile: User ID is None.")
        st.error("Cannot update profile. Please log in again.")
        return

    payload = {"about_section": about_section}
    endpoint = f"/users/{user_id}"
    response = send_data(endpoint, payload, method="PUT")
    if response:
        logger.info(f"Profile updated successfully for user {user_id}")
        st.success("Profile updated successfully!")
    else:
        logger.error(f"Failed to update profile for user {user_id}")
        st.error("Failed to update profile. Please try again.")



