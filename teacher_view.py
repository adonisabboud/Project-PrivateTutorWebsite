from server_requests import *
import streamlit as st
import logging

from update_meeting import handle_meeting_actions


def teacher_view():
    """Teacher Dashboard."""
    logger.info("Loading Teacher Dashboard.")
    st.subheader("Teacher Dashboard")
    options = ["Manage Meetings", "Edit Availability", "Edit Profile"]
    choice = st.sidebar.radio("Menu", options)

    if choice == "Manage Meetings":
        st.subheader("Your Meetings")
        try:
            teacher_meetings = get_my_meetings(st.session_state.user_id)
            if teacher_meetings:
                for meeting in teacher_meetings:
                    st.write(f"**Subject:** {meeting.get('topic', 'N/A')}")
                    st.write(f"**Student:** {meeting.get('student_name', 'N/A')}")
                    st.write(f"**Scheduled Time:** {meeting.get('scheduled_time', 'N/A')}")
                    action = st.radio(f"Actions for {meeting.get('topic')}", ["Approve", "Cancel"], key=meeting.get('id'))
                    if st.button(f"{action} Meeting: {meeting.get('topic')}", key=f"{action}_{meeting['id']}"):
                        handle_meeting_actions(meeting.get('id'), action)
                    st.write("---")
            else:
                logger.info("No meetings found for teacher.")
                st.info("No meetings found.")
        except Exception as e:
            logger.exception("Error loading meetings for teacher.")
            st.error("Failed to load meetings. Please try again later.")

    elif choice == "Edit Availability":
        st.subheader("Edit Your Availability")
        availability = st.text_area("Enter your availability (e.g., Monday 9-12 AM)")
        if st.button("Save Availability"):
            try:
                user_data = get_user_data(st.session_state.user_id)
                if not user_data:
                    st.error("Failed to fetch user data. Cannot update availability.")
                    return
                payload = {
                    "name": user_data.get("name"),
                    "about_section": user_data.get("about_section", ""),
                    "availability": availability
                }
                if send_data(f"/teachers/{st.session_state.user_id}", payload, method="PUT"):
                    logger.info(f"Availability updated for user {st.session_state.user_id}")
                    st.success("Availability updated successfully!")
                else:
                    logger.error(f"Failed to update availability for user {st.session_state.user_id}")
                    st.error("Failed to update availability. Please try again.")
            except Exception as e:
                logger.exception("Error updating availability.")
                st.error("An error occurred while updating availability. Please try again later.")

    elif choice == "Edit Profile":
        st.subheader("Edit Your Profile")
        about_section = st.text_area("About Me", placeholder="Write about yourself...")
        if st.button("Update Profile"):
            try:
                if send_data(f"/users/{st.session_state.user_id}", {"about_section": about_section}, method="PUT"):
                    logger.info(f"Profile updated for user {st.session_state.user_id}")
                    st.success("Profile updated successfully!")
                else:
                    logger.error(f"Failed to update profile for user {st.session_state.user_id}")
                    st.error("Failed to update profile. Please try again.")
            except Exception as e:
                logger.exception("Error updating profile.")
                st.error("An error occurred while updating your profile. Please try again later.")
