#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from datetime import datetime, date
import random
import google.generativeai as genai
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import (
    create_user_account,
    create_user_post,
    get_genai_advice,
    get_user_by_username,
    get_user_posts,
    get_user_profile,
    get_user_sensor_data,
    get_user_workouts,
    update_user_profile_details,
)
from community_page import display_community_page
from activity_page import display_activity_page

GEMINI_API_KEY = "AIzaSyCUwvjVDxFk75RHFbJ9ljnIvYnhilv6xqM"
def _clear_user_cached_state():
    """Clears session keys that are specific to a logged-in user."""
    for key in ["ai_advice_content", "ai_advice_timestamp", "ai_advice_image"]:
        st.session_state.pop(key, None)


def _display_auth_gate():
    """Shows login/signup UI and returns True only when authenticated."""
    st.title("Welcome")
    st.write("Log in with your username, or create a new account.")

    login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])

    with login_tab:
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_submitted = st.form_submit_button("Log In")

        if login_submitted:
            user = get_user_by_username(login_username)
            if user:
                st.session_state["user_id"] = user["user_id"]
                st.session_state["username"] = user["username"]
                _clear_user_cached_state()
                st.rerun()
            else:
                st.error("Invalid username. Please try again or sign up.")

    with signup_tab:
        with st.form("signup_form"):
            signup_name = st.text_input("Name", key="signup_name")
            signup_username = st.text_input("Username", key="signup_username")
            signup_submitted = st.form_submit_button("Sign Up")

        if signup_submitted:
            try:
                created_user = create_user_account(signup_name, signup_username)
                st.session_state["user_id"] = created_user["user_id"]
                st.session_state["username"] = created_user["username"]
                _clear_user_cached_state()
                st.success("Account created successfully.")
                st.rerun()
            except ValueError as err:
                st.error(str(err))
            except Exception:
                st.error("Could not create the account right now. Please try again.")

    return bool(st.session_state.get("user_id"))

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
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None

    if not st.session_state.get("user_id"):
        _display_auth_gate()
        return

    userId = st.session_state["user_id"]
    st.sidebar.title("Menu")
    if st.sidebar.button("Log Out"):
        st.session_state["user_id"] = None
        st.session_state["username"] = None
        _clear_user_cached_state()
        st.rerun()

    selection = st.sidebar.radio(
        "Go to",
        ["Home", "Profile", "Posts", "Activity Summary", "Recent Workouts", "AI Trainer Advice", "Community", "Activity"]
    )

    if selection == "Home":
        user_profile = get_user_profile(userId)
        if not user_profile:
            st.error("Could not load your profile. Please log in again.")
            st.session_state["user_id"] = None
            st.session_state["username"] = None
            _clear_user_cached_state()
            return
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
                    content = posts[0].get('content') or "No text content"
                    st.write(f"📢 Latest: *{content[:50]} ...*")

        with col3:
            st.subheader("Recent Activity")
            workout = get_user_workouts(userId)
            if workout:
                st.write("🔥 Calories Burned Today:" )
                st.write(f"{workout[0].get('calories_burned')} kcal")

        st.divider()
        st.subheader("Today's going to be a great day!")
        st.write("👈 Use the menu to dive deeper into your stats or community posts.")

    elif selection == "Profile":
        st.header('Profile')
        user_profile = get_user_profile(userId)
        if not user_profile:
            st.error('Could not load your profile.')
            return

        image_url_default = user_profile.get('profile_image') or ''
        raw_dob = user_profile.get('date_of_birth')

        if isinstance(raw_dob, datetime):
            dob_default = raw_dob.date()
        elif isinstance(raw_dob, date):
            dob_default = raw_dob
        else:
            try:
                dob_default = datetime.fromisoformat(str(raw_dob)).date() if raw_dob else date(2000, 1, 1)
            except (TypeError, ValueError):
                dob_default = date(2000, 1, 1)

        with st.form('profile_edit_form'):
            updated_image_url = st.text_input('Profile Image URL', value=image_url_default)
            updated_dob = st.date_input('Date of Birth', value=dob_default)
            update_profile_submitted = st.form_submit_button('Save Profile Changes')

        if update_profile_submitted:
            try:
                update_user_profile_details(userId, updated_image_url, updated_dob)
                st.success('Profile updated successfully.')
                st.rerun()
            except ValueError as err:
                st.error(str(err))
            except Exception:
                st.error('Could not update profile right now. Please try again.')
                
    elif selection == "Posts":
        st.header('Posts')
        user_profile = get_user_profile(userId)

        with st.expander("Create Post", expanded=False):
            with st.form("create_post_form"):
                post_content = st.text_area("Post text", placeholder="What do you want to share?")
                post_image_url = st.text_input("Image URL (optional)")
                create_post_submitted = st.form_submit_button("Create Post")

            if create_post_submitted:
                try:
                    create_user_post(userId, post_content, post_image_url)
                    st.success("Post created successfully.")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))
                except Exception:
                    st.error("Could not create the post right now. Please try again.")

        st.subheader("Your Posts")

        posts = get_user_posts(userId)
        if not posts:
            st.info('No posts yet. Create your first post above.')
        for post in posts:
            display_post(
                username=user_profile['username'],
                user_image=user_profile['profile_image'],
                timestamp=post['timestamp'],
                content=post['content'],
                post_image=post['image'],
                commenter_username=user_profile['username'])

    elif selection == "Activity Summary":
        st.header('Activity Summary')
        workouts = get_user_workouts(userId)
        display_activity_summary(workouts)
    
    elif selection == "Community":
        #st.header('Community')
        display_community_page(userId)
    
    elif selection == "Activity":
        #st.header('Activity')
        display_activity_page(userId)

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
                    model  = genai.GenerativeModel("gemini-2.5-flash-lite")
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
