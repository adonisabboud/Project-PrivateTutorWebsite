import streamlit as st
import requests
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get BASE_URL from the .env file
BASE_URL = os.getenv("BASE_URL")

# Check if BASE_URL is loaded properly
if not BASE_URL:
    st.error("BASE_URL not found in the environment variables. Please configure it in your .env file.")
    raise ValueError("BASE_URL is not set in the .env file.")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def handle_response(response, success_message=None):
    try:
        if response.status_code in [200, 201]:
            if success_message:
                st.success(success_message)
            return response.json()  # Return the parsed response
        else:
            # Handle error responses
            error_message = response.json().get("message", response.text)
            logger.error(f"API Error: {response.status_code} - {response.text}")
            st.error(f"Error: {error_message}")
            return None
    except Exception as e:
        logger.exception(f"Failed to handle API response: {e}")
        st.error("An unexpected error occurred while processing the server response.")
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


def send_data(endpoint, data=None, method="POST"):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.get('token', '')}",
            "Content-Type": "application/json"
        }
        url = f"{BASE_URL}{endpoint}"
        logger.info(f"Sending {method} request to {url} with data: {data}")

        response = requests.request(method, url, headers=headers, json=data)
        logger.debug(f"API Response: {response.status_code} - {response.text}")

        return handle_response(response)
    except requests.exceptions.RequestException as e:
        logger.exception(f"Request to {endpoint} failed: {e}")
        st.error("A network error occurred. Please check your connection and try again.")
        return None


# def send_data(endpoint, data=None, method="POST"):
#     """
#     Send data to a specified API endpoint using the desired HTTP method.
#
#     Args:
#         endpoint (str): The API endpoint to send the data to.
#         data (dict, optional): The payload to send to the server.
#         method (str): The HTTP method to use (e.g., "POST", "PUT", "DELETE").
#
#     Returns:
#         dict or None: The server's response (parsed JSON) on success; None on failure.
#     """
#     try:
#         headers = {
#             "Authorization": f"Bearer {st.session_state.get('token', '')}",
#             "Content-Type": "application/json"
#         }
#         url = f"{BASE_URL}{endpoint}"
#         logger.info(f"Sending {method} request to {url} with data: {data}")
#
#         if method == "POST":
#             response = requests.post(url, headers=headers, json=data)
#         elif method == "PUT":
#             response = requests.put(url, headers=headers, json=data)
#         elif method == "DELETE":
#             response = requests.delete(url, headers=headers, json=data)
#         else:
#             logger.error(f"Unsupported HTTP method: {method}")
#             st.error(f"Unsupported HTTP method: {method}")
#             return None
#
#         # Handle response
#         return handle_response(response)
#     except requests.exceptions.RequestException as e:
#         logger.exception(f"Request to {endpoint} failed: {e}")
#         st.error("A network error occurred. Please check your connection and try again.")
#         return None


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
def request_meeting_with_teacher(teacher):
    """
    Create a meeting instance using the selected teacher's data and provided meeting details.

    Args:
        teacher (dict): The teacher's JSON data.
    """
    try:
        st.subheader(f"Request Meeting with {teacher.get('name', 'N/A')}")

        # Allow the student to input meeting details
        meeting_subject = st.text_input("Meeting Subject", help="Enter the subject of the meeting.")
        meeting_location = st.text_input("Meeting Location", help="Enter the meeting location.")
        start_time = st.time_input("Start Time", help="Set the meeting's start time.")
        finish_time = st.time_input("Finish Time", help="Set the meeting's end time.")

        if st.button("Request Meeting"):
            if not meeting_subject or not meeting_location:
                st.warning("Please provide both subject and location for the meeting.")
                return

            if finish_time <= start_time:
                st.warning("Finish time must be after start time.")
                return

            # Build the meeting payload
            meeting_data = {
                "location": meeting_location,
                "start_time": start_time.isoformat(),
                "finish_time": finish_time.isoformat(),
                "subject": meeting_subject,
                "people": [
                    {"id": teacher['id'], "role": "Teacher", "name": teacher.get('name', 'N/A')},
                    {"id": st.session_state.get("user_id"), "role": "Student",
                     "name": st.session_state.get("user_name")}
                ],
                "attached_files": []  # Optional, leave empty for now
            }

            # Send the meeting request to the `/meetings/` endpoint
            response = send_data("/meetings/", meeting_data)
            if response:
                logger.info(f"Meeting created successfully: {response}")
                st.success("Meeting successfully created!")
            else:
                logger.error(f"Failed to create meeting: {meeting_data}")
                st.error("Failed to create the meeting. Please try again.")
    except Exception as e:
        logger.exception(f"Error requesting meeting with teacher {teacher.get('id')}: {e}")
        st.error("An unexpected error occurred. Please try again.")


def get_my_meetings(user_id):  #
    try:
        logger.info(f"Fetching meetings for user ID: {user_id}")
        if not user_id:
            logger.error("User ID is None. Cannot fetch meetings.")
            st.error("Please log in to view your meetings.")
            return []

        endpoint = f"/meetings/user/{user_id}"  # we dont have the endpoint we want to get all meeting and go over
        # them and append the relevant meetings.
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
        st.error("Failed to update profilee. Please try again.")


def fetch_user_meetings(user_id):
    """Fetch and filter meetings where the user is a participant."""
    try:
        response = fetch_data("/meetings/")  # Fetch all meetings
        if not response or not isinstance(response, list):
            st.error("Failed to fetch meetings or no meetings found.")
            return []

        # Filter meetings where user_id is in the 'people' list
        user_meetings = [meeting for meeting in response if user_id in meeting.get("people", [])]
        return user_meetings
    except Exception as e:
        st.error(f"An error occurred while fetching meetings: {e}")
        return []


def get_user_data(user_id):
    """
    Fetches user data from the API using the user's ID.

    Args:
        user_id (str): The ID of the user to fetch.

    Returns:
        dict: User data on successful fetch, or None on failure.
    """
    if not user_id:
        logger.error("User ID is None. Cannot fetch user data.")
        st.error("User ID is required to fetch user data.")
        return None

    try:
        # Construct the endpoint to fetch user data
        endpoint = f"/users/id/{user_id}"
        logger.info(f"Fetching data for user ID: {user_id}")

        # Make the API call
        user_data = fetch_data(endpoint)

        # Optionally, process or log the user data if needed
        if user_data:
            logger.info(f"Retrieved data for user {user_id}: {user_data}")
        else:
            logger.info(f"No data found for user {user_id}")

        return user_data
    except Exception as e:
        logger.exception(f"Error fetching data for user {user_id}: {e}")
        st.error("Failed to fetch user data. Please try again later.")
        return None


def check_existing_profile(profile_type):
    """Check if a profile already exists for the user by fetching all profiles of the given type and checking for user ID."""
    if profile_type == "Student":
        endpoint = "/students/"
    elif profile_type == "Teacher":
        endpoint = "/teachers/"
    else:
        raise ValueError("Invalid profile type specified")

    all_profiles = fetch_data(endpoint)
    print("Fetched profiles:", all_profiles)  # Debug output to see what is fetched

    if not all_profiles:  # Checks if list is empty or None
        st.error("No profiles found or failed to fetch profiles.")
        return None

    user_id = st.session_state.get('user_id')  # Safely get the user_id with a fallback
    if user_id is None:
        st.error("User ID not set in session state.")
        return None

    for profile in all_profiles:
        if profile.get("id") == user_id:
            return profile  # Profile exists

    return None  # No profile found
