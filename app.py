#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.sidebar.title("Menu")
    selection = st.sidebar.radio(
        "Go to",
        ["Home", "Posts", "Activity Summary", "Recent Workouts", "AI Trainer Advice"]
    )

    if selection == "Home":
        st.title("Welcome to the training app")
        st.write("Select a section from the menu on the left to get started.")

    elif selection == "Posts":
        st.header('Posts')
        user_profile = get_user_profile(userId)
        posts = get_user_posts(userId)
        for post in posts:
            display_post(
                username=user_profile['username'],
                user_image=user_profile['profile_image'],
                timestamp=post['timestamp'],
                content=post['content'],
                post_image=post['image'])

    elif selection == "Activity Summary":
        workouts = get_user_workouts(userId)
        display_activity_summary(workouts)

    elif selection == "Recent Workouts":
        workouts = get_user_workouts(userId)
        display_recent_workouts(workouts)

    elif selection == "AI Trainer Advice":
        advice = get_genai_advice(userId)
        display_genai_advice(advice['timestamp'], advice['content'], advice['image'])

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
