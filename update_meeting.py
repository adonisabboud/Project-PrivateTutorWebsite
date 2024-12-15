def handle_meeting_actions(meeting_id, action):
    """
    Handle meeting actions like Cancel or Approve.

    Args:
        meeting_id (str): The ID of the meeting.
        action (str): The action to perform (e.g., "Approve", "Cancel").

    Returns:
        None
    """
    try:
        status = "Approved" if action == "Approve" else "Canceled"
        if send_data(f"/meetings/{meeting_id}", {"status": status}, method="PUT"):
            logger.info(f"Meeting {action}d: {meeting_id}")
            st.success(f"Meeting {action}d successfully.")
        else:
            logger.error(f"Failed to {action} meeting: {meeting_id}")
            st.error(f"Failed to {action} the meeting.")
    except Exception as e:
        logger.exception(f"Error performing action '{action}' for meeting {meeting_id}")
        st.error(f"An error occurred while trying to {action} the meeting. Please try again.")
