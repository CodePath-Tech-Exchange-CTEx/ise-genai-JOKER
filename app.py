#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from datetime import datetime
import random
#import google.generativeai as genai
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

GEMINI_API_KEY = "AIzaSyCUwvjVDxFk75RHFbJ9ljnIvYnhilv6xqM"
userId = 'user1'

FALLBACK_MOTIVATIONS = [
    "You've been putting in the work and it shows — consistency is your superpower. ",
    "Every rep, every step is building a stronger version of you. ",
    "For your next session, try adding 10% more weight or one extra set to keep pushing your limits. "
    "You've got this — now go make it count! 💪",
    "Your dedication to showing up is what separates you from the rest. ",
    "The effort you put in today is an investment your future self will thank you for. ",
    "Challenge yourself to beat your last personal best — even by just one rep. ",
    "Greatness is built one session at a time. Let's go!",
    "Look how far you've come — that progress didn't happen by accident. ",
    "Your body is adapting and getting stronger with every workout. ",
    "Next session, focus on your form and slow down the eccentric phase for maximum gains. ",
    "The best workout is always the next one. Bring the energy!",
    "Every session you complete is proof that your commitment is real. ",
    "The habits you're building now will carry you for life. ",
    "Try finishing your next workout with a 5-minute high-intensity finisher to torch extra calories. ",
    "Stay hungry, stay consistent — you're unstoppable!",
    "Your results are speaking for themselves — keep trusting the process. ",
    "Strength isn't just built in the gym, it's built in the moments you choose not to quit. ",
    "Push the pace on your next cardio session and see what your lungs are really capable of. ",
    "Champions are made on the days they don't feel like it. Today is that day!",
]

def display_app_page():
    """Displays the home page of the app."""
    st.sidebar.title("Menu")
    selection = st.sidebar.radio(
        "Go to",
        ["Home", "Posts", "Activity Summary", "Recent Workouts", "AI Trainer Advice"]
    )

    if selection == "Home":
        user_profile = get_user_profile(userId)
        st.title(f"Welcome back, {user_profile['username']}! 👋")
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Latest Advice")
            advice = get_genai_advice(userId)
            st.info(f"{advice['content'][:100]} ...") 
            
        with col2:
            st.subheader("Community")
            posts = get_user_posts(userId)
            if posts:
                # show a snippet of the most recent post
                st.write(f"📢 Latest: *{posts[0]['content'][:50]} ...*")

        with col3:
            st.subheader("Recent Activity")
            workout = get_user_workouts(userId)
            if workout:
                st.write("🔥 Calories Burned Today:" )
                st.write(f"{workout[0].get('calories_burned')} kcal")

        st.divider()
        st.subheader("Today's going to be a great day!")
        st.write("👈 Use the menu to dive deeper into your stats or community posts.")

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
        if "ai_advice_content" not in st.session_state:
 
            # Gather user context
            user_profile = get_user_profile(userId)
            workouts     = get_user_workouts(userId)
 
            username = user_profile.get("username", "the user")
 
            # Build prompt 
            prompt = f"""You are an expert personal fitness trainer and motivational coach.
Your job is to give {username} a personalised, energetic, and actionable workout motivation message.
 
Here is their recent workout history:
{workouts}
 
 
Based on this data, write a motivational message (3-5 sentences) that:
- Acknowledges something specific from their recent activity or stats
- Highlights a genuine strength or positive trend you can see
- Gives one concrete, encouraging tip or challenge for their next session
- Ends on a high-energy, uplifting note
 
Keep the tone like a knowledgeable coach who knows them personally. Be specific — avoid generic filler phrases."""
 
            #  Call Gemini
            with st.spinner("Getting your personalised advice..."):
                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    model  = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)
                    ai_content = response.text
                except Exception as e:
                    ai_content = random.choice(FALLBACK_MOTIVATIONS)
 
            
            st.session_state["ai_advice_content"]   = ai_content
            st.session_state["ai_advice_timestamp"] = datetime.now()
 
        display_genai_advice(
            timestamp = st.session_state["ai_advice_timestamp"],
            content   = st.session_state["ai_advice_content"],
            image     = None,   
        )

if __name__ == '__main__':
    display_app_page()
