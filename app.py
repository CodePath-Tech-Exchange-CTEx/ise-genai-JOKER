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
from data_fetcher import (
    add_friend,
    authenticate_user,
    append_post_comment,
    create_user_account,
    create_user_post,
    get_genai_advice,
    get_people_you_may_know,
    get_user_posts,
    get_user_profile,
    get_user_sensor_data,
    get_user_workouts,
    increment_post_likes,
    update_user_profile_details,
    update_user_password,
)
from pages import  (
    display_profile_page, 
    display_posts_page,
    display_community_page,
    display_activity_page,
    display_recent_workouts,
    display_recent_workouts_with_add_form,
    display_genai_advice,
)


GEMINI_API_KEY = "AIzaSyCUwvjVDxFk75RHFbJ9ljnIvYnhilv6xqM"

st.set_page_config(
    page_title="The Training Club",
    page_icon="🏃",
)

# ---------------------------------------------------------
# GLOBAL THEME INJECTION
# ---------------------------------------------------------
GLOBAL_THEME_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
<style>
    /* Hide the default Streamlit auto-generated page navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Force the sidebar content to move up and ignore the deleted nav's ghost padding */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important; 
    }
    
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }

    /* Base App Theme */
    .stApp, .stAppHeader {
        background-color: #0d0d0d !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0d0d0d !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* Native Typography Overrides */
    h1, h2, h3, .st-emotion-cache-10trblm {
        font-family: 'Bebas Neue', sans-serif !important;
        color: #ffffff !important;
        letter-spacing: 0.05em;
    }
    p, span, label {
        font-family: 'DM Sans', sans-serif;
        color: #bcbcbc;
    }

    /* Form Inputs */
    .stTextInput input, .stTextArea textarea, .stDateInput input { 
        background-color: rgba(255,255,255,0.03) !important; 
        color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.1) !important; 
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus { 
        border-color: #fa114f !important; 
        box-shadow: 0 0 0 1px #fa114f !important;
    }

    /* Standard Buttons */
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #0d0d0d !important;
        color: #bcbcbc !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px;
        transition: all 0.2s ease;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: bold;
    }
    div[data-testid="stButton"] > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        border-color: #fa114f !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(250, 17, 79, 0.2);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 20px; }
    .stTabs [data-baseweb="tab"] { color: #bcbcbc; font-family: 'Bebas Neue', sans-serif; font-size: 1.2em; letter-spacing: 0.05em; padding: 10px 0; }
    .stTabs [aria-selected="true"] { color: #fa114f !important; border-bottom-color: #fa114f !important; border-bottom-width: 3px !important; }
    
    /* Dividers */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* ---------------------------------------------------------
     * SIDEBAR MENU UPGRADE
     * --------------------------------------------------------- */
    
    /* 1. Hide the ugly radio dot */
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-of-type {
        display: none !important;
    }
    
    /* 2. Style the invisible box around the menu item into a pill */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        width: 100% !important; /* <--- THE FIX: Forces the clickable area to span the entire sidebar */
        background-color: transparent !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        margin-bottom: 6px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        border-left: 4px solid transparent !important; 
        display: flex !important;
        align-items: center !important;
    }

    /* Ensure the inner container fills the new wide label so the whole thing is clickable */
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:last-of-type {
        width: 100% !important;
        cursor: pointer !important;
    }
    
    /* 3. The Hover State (Making it POP) */
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-left: 4px solid rgba(255, 255, 255, 0.2) !important; /* Subtle preview border */
    }
    
    /* Make the text brighten up on hover */
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover p {
        color: #ffffff !important;
    }
    
    /* 4. The Active/Selected State */
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked),
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
        background-color: rgba(250, 17, 79, 0.1) !important;
        border-left: 4px solid #fa114f !important;
        border-radius: 4px 8px 8px 4px !important; /* Flat on the left, rounded on the right */
    }
    
    /* Make the text white and bold when active */
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Ensure typography matches */
    [data-testid="stSidebar"] div[role="radiogroup"] p {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.1em !important;
        color: #bcbcbc !important;
        margin: 0 !important;
        padding: 4px 0 !important;
        transition: color 0.2s ease;
    }
    
    /* 5. Custom Styling for the Sidebar 'Log Out' Button (Bulletproof) */
    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        border-color: rgba(250, 17, 79, 0.2) !important;
        color: #fa114f !important;
        margin-bottom: 24px !important; 
        
        /* CSS Firewall: Overrides any bleeding styles from the Posts page */
        border-radius: 8px !important;
        height: auto !important;
        min-height: 42px !important;
        width: 100% !important;
        padding: 4px 14px !important;
    }
    
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background-color: rgba(250, 17, 79, 0.1) !important;
        border-color: #fa114f !important;
        color: #ffffff !important;
        transform: none !important; /* Prevents the shrink-click effect from bleeding */
    }

    /* 1. Nuke the "Press Enter to submit form" text to fix the overlap */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* 2. Clean up the double focus ring on inputs */
    [data-baseweb="input"]:focus-within {
        /* Removes Streamlit's default blue/gray glow */
        box-shadow: 0 0 0 1px #fa114f !important; 
        /* Forces the outer container to use your pink branding */
        border-color: #fa114f !important;         
    }
    
    /* Ensure the inner input doesn't draw its own separate border */
    [data-baseweb="input"] input:focus {
        outline: none !important;
        border: none !important;
        box-shadow: none !important;
    }

        /* Add the interactive hover lift effect to the custom HTML cards */
    .dashboard-card {
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    .dashboard-card:hover {
        transform: translateY(-6px) !important;
        box-shadow: 0 0 0 1px #0d0d0d, 0 12px 30px rgba(250, 17, 79, 0.2) !important;
    }
</style>
"""

def create_dashboard_card(title, content, icon):
    """Helper to generate styled cards for the Home page dashboard"""
    return f"""
    <div class="dashboard-card"style="background: #0d0d0d; border-radius: 16px; padding: 24px; height: 100%;
                box-shadow: 0 0 0 1px rgba(255,255,255,0.06), 0 12px 30px rgba(0,0,0,0.5);
                display: flex; flex-direction: column; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5em;">{icon}</span>
            <span style="font-family: 'Bebas Neue', sans-serif; font-size: 1.5em; color: #ffffff; letter-spacing: 0.05em;">{title}</span>
        </div>
        <div style="width: 30px; height: 3px; background: linear-gradient(90deg, #fa114f, #ff6b35); border-radius: 2px;"></div>
        <div style="font-family: 'DM Sans', sans-serif; font-size: 0.95em; color: #bcbcbc; line-height: 1.6; font-style: italic;">
            {content}
        </div>
    </div>
    """

def _clear_user_cached_state():
    """Clears session keys that are specific to a logged-in user."""
    for key in ["ai_advice_content", "ai_advice_timestamp", "ai_advice_image"]:
        st.session_state.pop(key, None)


def _display_auth_gate():
    """Shows login/signup UI and returns True only when authenticated."""
    
    # Custom styled header for the auth gate
    st.markdown("""
    <div style="margin-top: 40px; margin-bottom: 30px; text-align: center;">
        <h1 style="font-size: 4em; line-height: 1; margin-bottom: 10px;">Welcome to the Club</h1>
        <p style="color: #bcbcbc; font-size: 1.1em;">Log in with your username, or create a new account to join.</p>
    </div>
    """, unsafe_allow_html=True)

    login_tab, signup_tab = st.tabs(["Log In", "Sign Up"])

    with login_tab:
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submitted = st.form_submit_button("Log In")

        if login_submitted:
            user = authenticate_user(login_username, login_password)
            if user:
                st.session_state["user_id"] = user["user_id"]
                st.session_state["username"] = user["username"]
                _clear_user_cached_state()
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again or sign up.")

    with signup_tab:
        with st.form("signup_form"):
            signup_name = st.text_input("Name", key="signup_name")
            signup_username = st.text_input("Username", key="signup_username")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_submitted = st.form_submit_button("Sign Up")

        if signup_submitted:
            try:
                created_user = create_user_account(signup_name, signup_username, signup_password)
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
    "For your next session, try adding 10% more weight or one extra set to keep pushing your limits. ",
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
    
    # Inject global CSS first
    st.markdown(GLOBAL_THEME_CSS, unsafe_allow_html=True)
    
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None

    if not st.session_state.get("user_id"):
        st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
        </style>
        """, unsafe_allow_html=True)
        _display_auth_gate()
        return

    userId = st.session_state["user_id"]
    st.sidebar.markdown("<h1 style='font-size: 2.5em; margin-bottom: 20px;'>Menu</h1>", unsafe_allow_html=True)
    
    if st.sidebar.button("Log Out", use_container_width=True):
        st.session_state["user_id"] = None
        st.session_state["username"] = None
        _clear_user_cached_state()
        st.rerun()

    selection = st.sidebar.radio(
        "Navigation",
        ["Home", "Profile", "Posts", "Activity", "Recent Workouts", "Community", "AI Trainer Advice"],
        label_visibility="collapsed"
    )

    if selection == "Home":
        user_profile = get_user_profile(userId)
        if not user_profile:
            st.error("Could not load your profile. Please log in again.")
            st.session_state["user_id"] = None
            st.session_state["username"] = None
            _clear_user_cached_state()
            return
            
        # Custom welcome header
        st.markdown(f"""
        <div style="margin-top: 20px; margin-bottom: 10px;">
            <h1 style="font-size: 3.5em; line-height: 1;">Welcome back, {user_profile['username']}! 👋</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            advice = get_genai_advice(userId)
            content = f"{advice['content'][:100]}..." if advice and 'content' in advice else "Keep pushing your limits. Greatness awaits."
            st.markdown(create_dashboard_card("Latest Advice", content, "🧠"), unsafe_allow_html=True)
            
        with col2:
            posts = get_user_posts(userId)
            if posts:
                content = posts[0].get('content') or "No text content"
                content = f"📢 Latest: <em>{content[:60]}...</em>"
            else:
                content = "No recent updates from your network."
            st.markdown(create_dashboard_card("Community", content, "🌐"), unsafe_allow_html=True)

        with col3:
            workout = get_user_workouts(userId)
            if workout:
                cal = workout[0].get('calories_burned')
                content = f"<span style='color:#ffffff; font-weight:bold; font-size: 1.2em;'>{cal} KCAL</span> burned in your last session."
            else:
                content = "Ready to start your next session?"
            st.markdown(create_dashboard_card("Activity", content, "🔥"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()
        
        st.markdown("<h2 style='font-size: 2.2em;'>People You Might Know</h2>", unsafe_allow_html=True)
        suggestions = get_people_you_may_know(userId, limit=5)

        if not suggestions:
            st.caption("No suggestions right now.")
        else:
            for person in suggestions:
                person_image = (person.get('profile_image') or '').strip()
                if person_image:
                    avatar_html = (
                        f"<img src=\"{person_image}\" alt=\"avatar\" "
                        "style=\"width: 44px; height: 44px; border-radius: 50%; object-fit: cover; border: 1px solid rgba(255,255,255,0.16);\">"
                    )
                else:
                    avatar_html = (
                        "<div style=\"width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.16);\">🏃</div>"
                    )
                # Styled user list row
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 15px 20px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        {avatar_html}
                        <div>
                            <div style="color: #ffffff; font-weight: bold; font-size: 1.1em;">{person.get('full_name', 'Unknown')}</div>
                            <div style="color: #bcbcbc; font-size: 0.9em; font-style: italic;">@{person.get('username', '')}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Button underneath or next to it (Streamlit limits mixing HTML & callbacks, so we keep the button native)
                col_btn, _ = st.columns([1, 4])
                with col_btn:
                    if st.button("Add Friend", key=f"add_friend_{person.get('user_id')}", use_container_width=True):
                        try:
                            add_friend(userId, person.get('user_id'))
                            st.success(f"Added @{person.get('username', '')} to your friends list.")
                            st.rerun()
                        except ValueError as err:
                            st.error(str(err))
                        except Exception as err:
                            st.error(f"Could not add friend right now: {err}")
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    elif selection == "Profile":
        display_profile_page(userId)
                
    elif selection == "Posts":
        st.markdown("<h1 style='font-size: 3em;'>Posts</h1>", unsafe_allow_html=True)
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

        st.markdown("<h2 style='font-size: 2em; margin-top: 30px;'>Your Posts</h2>", unsafe_allow_html=True)

        posts = get_user_posts(userId)
        if not posts:
            st.info('No posts yet. Create your first post above.')
        for post in posts:
            display_posts_page(
                username=user_profile['username'],
                user_image=user_profile['profile_image'],
                timestamp=post['timestamp'],
                content=post['content'],
                post_image=post['image'],
                commenter_username=user_profile['username'],
                post_id=post.get('post_id'),
                initial_likes=post.get('likes', 0),
                initial_comments=post.get('comments', []),
                on_like=increment_post_likes,
                on_comment=append_post_comment,
            )
 
    elif selection == "Community":
        display_community_page(userId)
    
    elif selection == "Activity":
        display_activity_page(userId)

    elif selection == "Recent Workouts":
        st.markdown("<h1 style='font-size: 3.5em; line-height: 1; margin-bottom: 20px;'>Recent Workouts</h1>", unsafe_allow_html=True)
        workouts = get_user_workouts(userId)
        display_recent_workouts_with_add_form(userId, workouts)

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
 
            # Call Gemini
            with st.spinner("Getting your personalised advice..."):
                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    model  = genai.GenerativeModel("gemini-2.0-flash-001")
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