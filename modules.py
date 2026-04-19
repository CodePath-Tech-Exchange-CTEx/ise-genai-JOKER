#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

import random
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from internals import create_component



# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    # create_component(data, html_file_name) # This function is in internals.py


import streamlit as st
from datetime import datetime

def display_post(
    username,
    user_image,
    timestamp,
    content,
    post_image,
    commenter_username="You",
    post_id=None,
    initial_likes=0,
    initial_comments=None,
    on_like=None,
    on_comment=None,
):
    """Displays a post with user information, content, and engagement stats."""
    
    # 1. Establish session state keys FIRST so we can use current values in the HTML
    post_key = post_id if post_id else f"{username}|{timestamp}|{content[:10]}"
    comments_key = f"comments_{post_key}"
    likes_key = f"likes_{post_key}"
    new_comment_key = f"new_comment_{post_key}"
    clear_flag_key = f"clear_new_comment_{post_key}"
    show_comments_key = f"show_comments_{post_key}"

    if comments_key not in st.session_state:
        st.session_state[comments_key] = list(initial_comments or [])
    if likes_key not in st.session_state:
        st.session_state[likes_key] = int(initial_likes or 0)
    if new_comment_key not in st.session_state:
        st.session_state[new_comment_key] = ""
    if clear_flag_key not in st.session_state:
        st.session_state[clear_flag_key] = False
    if show_comments_key not in st.session_state:
        st.session_state[show_comments_key] = False

    if st.session_state[clear_flag_key]:
        st.session_state[new_comment_key] = ""
        st.session_state[clear_flag_key] = False

    # Grab live counts and format grammar (Like vs Likes)
    current_likes = st.session_state[likes_key]
    current_comments = len(st.session_state[comments_key])
    
    like_text = "1 Like" if current_likes == 1 else f"{current_likes} Likes"
    comment_text = "1 Comment" if current_comments == 1 else f"{current_comments} Comments"

    # 2. Clean up the timestamp
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        formatted_time = dt.strftime("%B %d, %Y  ·  %I:%M %p")
    except:
        formatted_time = str(timestamp).split(".")[0] # Fallback if parsing fails

    # 3. Only build the image HTML if an image exists
    image_html = ""
    if post_image and str(post_image).strip():
        image_html = f'<img src="{post_image}" alt="Post image" class="post-image">'

    # 4. Generate the HTML card
    post_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
    <style>
      .post {{
        background: #0d0d0d;
        border-radius: 16px;
        padding: 30px 30px 15px 30px;
        margin-bottom: 15px;
        font-family: 'DM Sans', sans-serif;
        max-width: 680px; 
        margin-left: auto;
        margin-right: auto;
        box-shadow: 
          0 0 0 1px rgba(255,255,255,0.06), 
          0 24px 60px rgba(0,0,0,0.6);
      }}
      .post-header {{
        display: flex;
        align-items: center;
        margin-bottom: 20px;
      }}
      .profile-pic {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
        margin-right: 15px;
        border: 2px solid rgba(250, 17, 79, 0.3);
        object-fit: cover;
      }}
      .username {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.8em;
        letter-spacing: 0.05em;
        color: #ffffff;
        line-height: 1;
      }}
      .timestamp {{
        color: #657786;
        font-size: 0.8em;
        letter-spacing: 0.04em;
        margin-top: 4px;
      }}
      .post-content {{
        margin-bottom: 10px;
      }}
      .post-content p {{
        color: #e1e8ed;
        font-size: 1.1em;
        line-height: 1.6;
        margin: 0;
      }}
      .post-image {{
        max-width: 100%;
        border-radius: 12px;
        margin-top: 15px;
        border: 1px solid rgba(255,255,255,0.06);
      }}
      .post-divider {{
        height: 1px;
        background-color: rgba(255,255,255,0.07);
        margin-top: 20px;
      }}
    </style>

    <div class="post">
      <div class="post-header">
        <img src="{user_image}" alt="User" class="profile-pic" onerror="this.src='https://via.placeholder.com/50/222222/FFFFFF?text=?'">
        <div>
          <div class="username">{username}</div>
          <div class="timestamp">{formatted_time}</div>
        </div>
      </div>
      <div class="post-content">
        <p>{content}</p>
        {image_html}
      </div>
      <div class="post-divider"></div>
    </div>
    """
    st.markdown(post_html, unsafe_allow_html=True)

    # 5. Callbacks
    def _post_comment():
        new_comment = st.session_state.get(new_comment_key, "").strip()
        if new_comment:
            comment_value = f"{commenter_username}: {new_comment}"
            st.session_state[comments_key].append(comment_value)
            if on_comment and post_id:
                on_comment(post_id, comment_value)
        st.session_state[clear_flag_key] = True

    def _like_post():
        st.session_state[likes_key] = int(st.session_state.get(likes_key, 0)) + 1
        if on_like and post_id:
            on_like(post_id)

    def _cancel_comment():
        st.session_state[clear_flag_key] = True
        st.session_state[show_comments_key] = False

    def _toggle_comments():
        st.session_state[show_comments_key] = not st.session_state[show_comments_key]

    # 6. Streamlit Action Buttons (Now with max-content boundary protection)
    st.markdown(
      """
      <style>
        div[data-testid="stButton"] > button {
          background-color: rgba(255,255,255,0.03) !important;
          color: #bcbcbc !important;
          border: 1px solid rgba(255,255,255,0.05) !important;
          border-radius: 9999px !important;
          padding: 6px 20px !important; 
          display: inline-flex !important;
          align-items: center !important;
          justify-content: center !important;
          transition: all 0.2s ease;
          width: 100% !important;
          min-width: max-content !important; /* <--- THIS PREVENTS THE SPILLOVER */
          box-shadow: none !important; 
        }
        
        /* The Hover State */
        div[data-testid="stButton"] > button:hover {
          border-color: #fa114f !important;
          color: #ffffff !important;
          background-color: rgba(250, 17, 79, 0.1) !important;
        }

        /* The Click / Active State */
        div[data-testid="stButton"] > button:active {
          transform: scale(0.96) !important; 
          background-color: rgba(250, 17, 79, 0.2) !important;
        }

        /* Kill the sticky focus ring */
        div[data-testid="stButton"] > button:focus {
          outline: none !important;
          box-shadow: none !important;
        }

        /* Force button back to normal state if focused but NOT hovered */
        div[data-testid="stButton"] > button:focus:not(:hover) {
          border-color: rgba(255,255,255,0.05) !important;
          color: #bcbcbc !important;
          background-color: rgba(255,255,255,0.03) !important;
        }

        div[data-testid="stButton"] > button > div,
        div[data-testid="stButton"] p {
          font-family: 'DM Sans', sans-serif !important;
          font-size: 0.9em !important;
          font-weight: 500 !important;
          margin: 0 !important;
          padding: 0 !important;
          line-height: normal !important; 
          white-space: nowrap !important;
          display: inline-flex !important;
          align-items: center !important;
          gap: 6px !important;
        }
      </style>
      """,
      unsafe_allow_html=True,
    )

    # Gave the comments column a slightly wider ratio to accommodate the longer word
    spacer_left, controls_col1, controls_col2, spacer_right = st.columns([0.5, 1.5, 2.0, 4.0])
    
    with controls_col1:
        st.button(
            f"❤️ {like_text}",
            key=f"like_btn_{post_key}",
            use_container_width=True,
            on_click=_like_post,
        )
    with controls_col2:
        st.button(
            f"💬 {comment_text}",
            key=f"toggle_btn_{post_key}",
            use_container_width=True,
            on_click=_toggle_comments,
        )

    # 7. Comments Section
    if st.session_state[show_comments_key]:
        st.markdown('<p style="color: #ffffff; font-family: \'DM Sans\', sans-serif; margin-top: 15px;"><strong>Comments</strong></p>', unsafe_allow_html=True)
        st.text_area(
            "Add a comment",
            key=new_comment_key,
            placeholder="Write a comment...",
            label_visibility="collapsed",
        )

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            st.button(
                "Post",
                key=f"post_{post_key}",
                use_container_width=True,
                on_click=_post_comment,
            )

        with action_col2:
            st.button(
                "Cancel",
                key=f"cancel_{post_key}",
                use_container_width=True,
                on_click=_cancel_comment,
            )

        st.caption("Previous comments")
        if st.session_state[comments_key]:
            for old_comment in st.session_state[comments_key]:
                if isinstance(old_comment, dict):
                    old_comment_username = old_comment.get("username", "User")
                    old_comment_text = old_comment.get("text", "")
                    st.markdown(f'<span style="color:#bcbcbc">- <strong>{old_comment_username}</strong>: {old_comment_text}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span style="color:#bcbcbc">- {old_comment}</span>', unsafe_allow_html=True)
        else:
            st.caption("No comments yet.")


def display_activity_summary(workouts_list):
    """Displays the total metrics of the user's workout (number of workouts, total time spent, total calories burned)
    
    Arg:
        workouts_list: list of workouts.
    """
    
    total_workouts = str(len(workouts_list)) + ' sessions' if len(workouts_list) > 1 else str(len(workouts_list)) + ' session'
    total_minutes = sum(w.get('duration', 0) for w in workouts_list)
    time_val = f"{total_minutes // 60}h {total_minutes % 60}m" if total_minutes > 60 else f"{total_minutes}m"
    total_calories = sum(w.get('calories_burned', 0) for w in workouts_list)
    calorie_goal = 600

    # calculate ring completion (0 to 100)
    percent = min(int((total_calories / calorie_goal) * 100), 100)
    
    # calculate SVG stroke-dasharray (Circumference is 2 * pi * r)
    # Scaled up: for r=65, circumference is ~408
    offset = 408 - (408 * percent / 100)

    html_content = f"""
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
    <style>
      .activity-card {{
        background: #0d0d0d;
        border-radius: 16px;
        padding: 50px 60px;
        margin: 20px auto;
        font-family: 'DM Sans', sans-serif;
        max-width: 680px; /* Matched to AI Advice card */
        display: flex;
        align-items: center;
        gap: 60px; /* Increased gap for larger card */
        box-shadow: 
          0 0 0 1px rgba(255,255,255,0.06), 
          0 24px 60px rgba(0,0,0,0.6);
        animation: adviceFadeUp 0.5s cubic-bezier(.22,.68,0,1.2) both;
      }}
      .ring-container {{
        position: relative;
        width: 160px; /* Scaled up from 120px */
        height: 160px;
      }}
      .ring-svg {{
        transform: rotate(-90deg);
      }}
      .ring-bg {{
        fill: none;
        stroke: rgba(255,255,255,0.05);
        stroke-width: 14; /* Thicker ring */
      }}
      .ring-progress {{
        fill: none;
        stroke: url(#activity-gradient);
        stroke-width: 14; /* Thicker ring */
        stroke-linecap: round;
        transition: stroke-dashoffset 1s cubic-bezier(0.4, 0.0, 0.2, 1);
      }}
      .percent-text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -45%);
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.4em; /* Scaled up */
        color: #ffffff;
        letter-spacing: 0.05em;
      }}
      .info-container {{
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 20px; /* More breathing room between stats */
      }}
      .stat-label {{
        color: #fa114f;
        font-size: 0.8em; /* Scaled up */
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.14em;
      }}
      .stat-value {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.4em; /* Scaled up */
        color: #ffffff;
        margin-top: 6px;
        line-height: 1;
        letter-spacing: 0.05em;
      }}
      .stat-sub {{
        font-family: 'DM Sans', sans-serif;
        font-size: 0.4em;
        color: #484848;
        letter-spacing: 0.02em;
      }}
      
      /* Mobile responsiveness for the larger card */
      @media (max-width: 600px) {{
        .activity-card {{
          flex-direction: column;
          padding: 40px 30px;
          gap: 40px;
          text-align: center;
        }}
      }}
    </style>

    <div class="activity-card">
      <div class="ring-container">
        <svg class="ring-svg" width="160" height="160">
          <defs>
            <linearGradient id="activity-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#fa114f" />
              <stop offset="100%" stop-color="#ff6b35" />
            </linearGradient>
          </defs>
          <circle class="ring-bg" cx="80" cy="80" r="65"></circle>
          <circle class="ring-progress" cx="80" cy="80" r="65" 
                  style="stroke-dasharray: 408; stroke-dashoffset: {offset};"></circle>
        </svg>
        <div class="percent-text">{percent}%</div>
      </div>
      <div class="info-container">
        <div>
            <div class="stat-label">Total Workouts</div>
            <div class="stat-value">{total_workouts}</div>
        </div>
        <div>
            <div class="stat-label">Time Spent</div>
            <div class="stat-value">{time_val}</div>
        </div>
        <div>
            <div class="stat-label">Move Goal</div>
            <div class="stat-value">{total_calories} <span class="stat-sub">/ {calorie_goal} KCAL</span></div>
        </div>
      </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)


def display_recent_workouts(workouts_list):
    """Displays a list of recent workouts as styled HTML cards instead of a raw dataframe."""
    if not workouts_list or len(workouts_list) == 0:
        st.info("No recent workouts found. Start your fitness journey today!")
        return
    
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
    <style>
      .recent-header {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.2em;
        letter-spacing: 0.06em;
        color: #ffffff;
        margin: 0 0 14px 0;
        line-height: 1.05;
      }
      .recent-divider {
        width: 44px;
        height: 3px;
        background: linear-gradient(90deg, #fa114f, #ff6b35);
        border-radius: 2px;
        margin-bottom: 20px;
      }
      .workout-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
      }
      .workout-card:hover {
        transform: translateY(-2px);
        border-color: rgba(250, 17, 79, 0.4);
        background: rgba(255,255,255,0.04);
      }
      .workout-date {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.6em;
        color: #ffffff;
        letter-spacing: 0.05em;
        line-height: 1;
      }
      .workout-time {
        font-family: 'DM Sans', sans-serif;
        color: #bcbcbc;
        font-size: 0.85em;
        margin-top: 6px;
      }
      .workout-stats {
        display: flex;
        gap: 30px;
      }
      .stat-item {
        text-align: right;
      }
      .stat-val {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.6em;
        color: #ffffff;
        letter-spacing: 0.05em;
        line-height: 1;
      }
      .stat-val span {
        color: #fa114f;
      }
      .stat-lbl {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.7em;
        color: #657786;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 4px;
        font-weight: bold;
      }
    </style>
    <h2 class="recent-header">Recent Workouts</h2>
    <div class="recent-divider"></div>
    """, unsafe_allow_html=True)
    
    for w in workouts_list:
        # Parse start and end timestamps safely
        start_str = w.get('start_timestamp', '')
        end_str = w.get('end_timestamp', '')
        
        display_date = "Unknown Date"
        time_range = ""
        duration_mins = w.get('duration', 0)

        try:
            if start_str:
                start_dt = datetime.fromisoformat(str(start_str).replace('Z', '+00:00'))
                display_date = start_dt.strftime("%b %d, %Y").upper()
                time_range = start_dt.strftime("%I:%M %p")
                
                # If we don't have a hardcoded duration, try to calculate it
                if not duration_mins and end_str:
                    end_dt = datetime.fromisoformat(str(end_str).replace('Z', '+00:00'))
                    duration_mins = int((end_dt - start_dt).total_seconds() / 60)
                    time_range += f" - {end_dt.strftime('%I:%M %p')}"
        except ValueError:
            display_date = str(start_str).split()[0] if start_str else "Unknown"

        steps = w.get('steps', 0)
        distance = w.get('distance', 0)
        calories = w.get('calories_burned', 0)

        # Build the stats dynamically based on what data exists
        stats_html = ""
        if duration_mins:
            stats_html += f'<div class="stat-item"><div class="stat-val"><span>{duration_mins}</span></div><div class="stat-lbl">Mins</div></div>'
        if distance:
            stats_html += f'<div class="stat-item"><div class="stat-val"><span>{distance}</span></div><div class="stat-lbl">Distance</div></div>'
        if steps:
            stats_html += f'<div class="stat-item"><div class="stat-val"><span>{steps:,}</span></div><div class="stat-lbl">Steps</div></div>'
        if calories:
            stats_html += f'<div class="stat-item"><div class="stat-val"><span>{calories}</span></div><div class="stat-lbl">Cals</div></div>'

        card_html = f"""
        <div class="workout-card">
            <div>
                <div class="workout-date">{display_date}</div>
                <div class="workout-time">&#128336; {time_range}</div>
            </div>
            <div class="workout-stats">
                {stats_html}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

MOTIVATIONAL_IMAGES = [
    "https://images.unsplash.com/photo-1558611848-73f7eb4001a1",
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
    "https://images.unsplash.com/photo-1599058917212-d750089bc07e",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
]
 
 
def display_genai_advice(timestamp, content, image):
    """Displays AI-generated workout advice as a rich, styled HTML card.
 
    Features a dark athletic aesthetic with a hero image, animated glowing
    badge, bold typography, and a formatted timestamp footer.
 
    If no image is provided (or it is falsy), a random image is selected
    from the built-in MOTIVATIONAL_IMAGES pool on each call.
 
    Args:
        timestamp: A datetime object representing when the advice was generated.
        content: The text content of the AI advice.
        image: A URL string for the hero image, or None.
    """
    formatted_time = timestamp.strftime("%B %d, %Y  ·  %I:%M %p")
    resolved_image = random.choice(MOTIVATIONAL_IMAGES)
 
    image_section = ""
    if resolved_image:
        image_section = f"""
        <div class="hero-image-wrapper">
            <img src="{resolved_image}" alt="Workout motivation" class="hero-image" />
            <div class="hero-overlay"></div>
        </div>
        """
 
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
 
    body {{
      background: transparent;
      padding: 8px 0 12px 0;
    }}
 
    .advice-card {{
      background: #0d0d0d;
      border-radius: 16px;
      overflow: hidden;
      max-width: 680px;
      margin: 0 auto;
      font-family: 'DM Sans', sans-serif;
      box-shadow:
        0 0 0 1px rgba(255,255,255,0.06),
        0 24px 60px rgba(0,0,0,0.6);
      animation: adviceFadeUp 0.5s cubic-bezier(.22,.68,0,1.2) both;
    }}
 
    @keyframes adviceFadeUp {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
 
    /* Hero image */
    .hero-image-wrapper {{
      position: relative;
      width: 100%;
      height: 260px;
      overflow: hidden;
    }}
    .hero-image {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transform: scale(1.05);
      transition: transform 7s ease;
    }}
    .advice-card:hover .hero-image {{
      transform: scale(1.0);
    }}
    .hero-overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(
        to bottom,
        rgba(13,13,13,0.0)  0%,
        rgba(13,13,13,0.6) 70%,
        rgba(13,13,13,1.0) 100%
      );
    }}
 
    /* Card body */
    .advice-body {{
      padding: 26px 30px 30px;
    }}
 
    /* AI badge */
    .ai-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(250, 17, 79, 0.10);
      border: 1px solid rgba(250, 17, 79, 0.30);
      border-radius: 999px;
      padding: 5px 15px 5px 11px;
      margin-bottom: 20px;
    }}
    .ai-badge-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #fa114f;
      box-shadow: 0 0 8px 2px rgba(250,17,79,0.55);
      animation: badgePulse 2s ease-in-out infinite;
      flex-shrink: 0;
    }}
    @keyframes badgePulse {{
      0%, 100% {{ box-shadow: 0 0 8px 2px rgba(250,17,79,0.55); }}
      50%       {{ box-shadow: 0 0 3px 1px rgba(250,17,79,0.20); }}
    }}
    .ai-badge-label {{
      font-size: 0.70em;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: #fa114f;
    }}
 
    /* Heading */
    .advice-heading {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 2.2em;
      letter-spacing: 0.06em;
      color: #ffffff;
      margin: 0 0 14px 0;
      line-height: 1.05;
    }}
 
    /* Red accent bar */
    .advice-divider {{
      width: 44px;
      height: 3px;
      background: linear-gradient(90deg, #fa114f, #ff6b35);
      border-radius: 2px;
      margin-bottom: 20px;
    }}
 
    /* Content text */
    .advice-content {{
      color: #bcbcbc;
      font-size: 0.97em;
      line-height: 1.80;
      margin: 0 0 26px 0;
      font-style: italic;
    }}
 
    /* Footer */
    .advice-footer {{
      display: flex;
      align-items: center;
      gap: 9px;
      border-top: 1px solid rgba(255,255,255,0.07);
      padding-top: 16px;
      color: #484848;
      font-size: 0.76em;
      letter-spacing: 0.04em;
    }}
    .advice-footer-icon {{
      font-size: 0.9em;
      opacity: 0.7;
    }}
  </style>
</head>
<body>
  <div class="advice-card">
    {image_section}
    <div class="advice-body">
 
      <div class="ai-badge">
        <span class="ai-badge-dot"></span>
        <span class="ai-badge-label">AI Trainer</span>
      </div>
 
      <h2 class="advice-heading">Your Workout Motivation</h2>
      <div class="advice-divider"></div>
 
      <p class="advice-content">{content}</p>
 
      <div class="advice-footer">
        <span class="advice-footer-icon">&#128336;</span>
        <span>Generated on {formatted_time}</span>
      </div>
 
    </div>
  </div>
</body>
</html>"""
 
    components.html(html, height=560)

def display_recent_workouts_with_add_form(user_id, workouts_list):
    """Displays an 'Add Workout' form followed by the recent workouts list.
    
    Args:
        user_id: The current user's ID for creating new workouts.
        workouts_list: List of workout dictionaries to display.
    """
    from data_fetcher import create_user_workout
    
    st.markdown("<h2 style='font-size: 2.2em; margin-bottom: 10px;'>Add New Workout</h2>", unsafe_allow_html=True)
    st.caption('Log a new workout to track your progress.')
    
    with st.expander("➕ Add Workout", expanded=False):
        with st.form("add_workout_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                distance = st.number_input(
                    "Distance (miles)",
                    min_value=0.0,
                    step=0.1,
                    format="%.1f",
                    help="Total distance covered during the workout"
                )
                calories = st.number_input(
                    "Calories Burned",
                    min_value=0.0,
                    step=10.0,
                    format="%.0f",
                    help="Estimated calories burned"
                )
            
            with col2:
                steps = st.number_input(
                    "Total Steps",
                    min_value=0,
                    step=100,
                    help="Number of steps taken"
                )
                workout_date = st.date_input(
                    "Workout Date",
                    help="Date when the workout occurred"
                )
            
            add_workout_submitted = st.form_submit_button("Log Workout", type="primary", use_container_width=True)
        
        if add_workout_submitted:
            if distance == 0 and steps == 0 and calories == 0:
                st.error("Please enter at least one workout metric (distance, steps, or calories).")
            else:
                try:
                    from datetime import datetime as dt
                    start_time = dt.combine(workout_date, dt.min.time())
                    new_workout = create_user_workout(
                        user_id=user_id,
                        total_distance=distance,
                        total_steps=int(steps),
                        calories_burned=calories,
                        start_timestamp=start_time
                    )
                    st.success("✅ Workout logged successfully!")
                    st.rerun()
                except ValueError as err:
                    st.error(f"Invalid input: {str(err)}")
                except Exception as err:
                    st.error(f"Could not log workout: {str(err)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    display_recent_workouts(workouts_list)
