#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from datetime import datetime
import random
import google.generativeai as genai
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

GEMINI_API_KEY = "AIzaSyBXMofrwmkOxQwrrpqHZLAKPnpgfF7wibw"
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
        st.header('Activity Summary')
        workouts = get_user_workouts(userId)
        display_activity_summary(workouts)

    elif selection == "Recent Workouts":
        workouts = get_user_workouts(userId)
        display_recent_workouts(workouts)

    elif selection == "AI Trainer Advice":
        advice = get_genai_advice(userId)
        display_genai_advice(advice['timestamp'], advice['content'], advice['image'])

    # st.title("Ready to level up your workout?")

    # MOTIVATIONAL_IMAGES = [
    #     "https://images.unsplash.com/photo-1558611848-73f7eb4001a1",
    #     "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
    #     "https://images.unsplash.com/photo-1599058917212-d750089bc07e",
    #     "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
    #     "https://images.unsplash.com/photo-1506744038136-46273834b3fb"
    # ]

    # user_context = st.text_area(
    #     "Tell the AI about your workout goals or current mood (optional):",
    #     placeholder="e.g. I'm feeling tired today and need motivation to hit the gym..."
    # )

    # if st.button("⚡ Generate Motivation"):
    #     with st.spinner("Getting your personalized motivation..."):
    #         try:
    #             genai.configure(api_key=GEMINI_API_KEY)
    #             model = genai.GenerativeModel("gemini-2.0-flash")

    #             prompt = (
    #                 "You are an energetic and motivating personal fitness coach. "
    #                 "Give a short, powerful motivational message (2-4 sentences) to help someone crush their workout today. "
    #                 "Be specific, uplifting, and use active language. "
    #                 + (f"The user says: {user_context}" if user_context.strip() else "Make it general but inspiring.")
    #             )

    #             response = model.generate_content(prompt)
    #             advice = response.text

    #         except Exception as e:
    #             advice = "Every rep counts. Every step matters. Show up today, because the version of you that didn't give up is waiting on the other side. Let's go! 💪"
    #             st.warning(f"AI unavailable, showing default motivation. ({e})")

    #         random_image = random.choice(MOTIVATIONAL_IMAGES)
    #         display_genai_advice(datetime.now(), advice, random_image)

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
