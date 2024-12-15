from server_requests import *
import streamlit as st
import logging



def student_view():
    """Student Dashboard."""
    logger.info("Loading Student Dashboard.")
    st.subheader("Student Dashboard")
    options = ["Available Teachers", "My Meetings", "Edit Profile"]
    choice = st.sidebar.radio("Menu", options)

    if choice == "Available Teachers":
        st.subheader("Available Teachers")
        try:
            teachers = fetch_data("/teachers/")
            if teachers:
                for teacher in teachers:
                    st.write(f"**Name:** {teacher.get('name', 'N/A')}")
                    st.write(f"**Subjects:** {', '.join(teacher.get('subjects', []))}")
                    if st.button(f"Request Meeting with {teacher.get('name')}", key=teacher.get("id")):
                        logger.info(f"Requesting meeting with teacher {teacher.get('id')}")
                        request_meeting_with_teacher(teacher.get("id"))
                    st.write("---")
            else:
                logger.info("No teachers found.")
                st.info("No teachers found.")
        except Exception as e:
            logger.exception("Error fetching teachers.")
            st.error("Failed to load teacher data. Please try again later.")

    elif choice == "My Meetings":
        st.subheader("Your Meetings")
        try:
            student_meetings = get_my_meetings(st.session_state.user_id)
            if student_meetings:
                for meeting in student_meetings:
                    st.write(f"**Subject:** {meeting.get('topic', 'N/A')}")
                    st.write(f"**Teacher:** {meeting.get('teacher_name', 'N/A')}")
                    st.write(f"**Scheduled Time:** {meeting.get('scheduled_time', 'N/A')}")
                    if st.button(f"Cancel Meeting: {meeting.get('topic')}", key=meeting.get('id')):
                        handle_meeting_actions(meeting.get('id'), "Cancel")
                    st.write("---")
            else:
                logger.info("No meetings found for student.")
                st.info("No meetings found.")
        except Exception as e:
            logger.exception("Error fetching meetings for student.")
            st.error("Failed to load meetings. Please try again later.")

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
