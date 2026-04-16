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


def display_post(username, user_image, timestamp, content, post_image, commenter_username="You"):
    """Displays a post with user information, content, and engagement stats.

    Args:
        username: The username of the post's author.
        user_image: The URL for the user's profile image.
        timestamp: The time the post was made.
        content: The text content of the post.
        post_image: The URL for the main image of the post.
        commenter_username: The username shown when posting comments.
    """
    likes = random.randint(0, 1000)

    post_html = f"""
    <style>
      .post {{
        border: 1px solid #e1e8ed;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        background-color: #fff;
      }}
      .post-header {{
        display: flex;
        align-items: center;
        margin-bottom: 10px;
      }}
      .profile-pic {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
        margin-right: 10px;
      }}
      .username {{
        font-weight: bold;
      }}
      .timestamp {{
        color: #657786;
        font-size: 0.9em;
        margin-left: auto;
      }}
      .post-content {{
        margin-bottom: 10px;
      }}
      .post-image {{
        max-width: 100%;
        border-radius: 10px;
        margin-top: 10px;
      }}
      .post-footer {{
        display: flex;
        align-items: center;
        gap: 20px;
        color: #657786;
      }}
      .footer-pill {{
        display: flex;
        align-items: center;
        gap: 5px;
        background: #fff;
        border: 1px solid #ccd6dd;
        border-radius: 8px;
        color: #657786;
        font-size: 1em;
        padding: 6px 10px;
      }}
      .footer-actions {{
        display: flex;
        gap: 8px;
      }}
    </style>

    <div class="post">
      <div class="post-header">
        <img src="{user_image}" alt="User profile image" class="profile-pic">
        <div>
          <div class="username">{username}</div>
          <div class="timestamp">{timestamp}</div>
        </div>
      </div>
      <div class="post-content">
        <p>{content}</p>
        <img src="{post_image}" alt="Post image" class="post-image">
      </div>
      <div class="post-footer">
        <div class="footer-actions">
          <span class="footer-pill"><span>&#10084;&#65039;</span> {likes} Likes</span>
        </div>
      </div>
    </div>
    """
    st.markdown(post_html, unsafe_allow_html=True)

    # Simple, stable per-post comment section rendered below the card.
    post_id = f"{username}|{timestamp}|{content}"
    comments_key = f"comments_{post_id}"
    new_comment_key = f"new_comment_{post_id}"
    clear_flag_key = f"clear_new_comment_{post_id}"
    show_comments_key = f"show_comments_{post_id}"

    if comments_key not in st.session_state:
      st.session_state[comments_key] = []
    if new_comment_key not in st.session_state:
      st.session_state[new_comment_key] = ""
    if clear_flag_key not in st.session_state:
      st.session_state[clear_flag_key] = False
    if show_comments_key not in st.session_state:
      st.session_state[show_comments_key] = False

    if st.session_state[clear_flag_key]:
      st.session_state[new_comment_key] = ""
      st.session_state[clear_flag_key] = False

    def _post_comment():
      new_comment = st.session_state.get(new_comment_key, "").strip()
      if new_comment:
        st.session_state[comments_key].append({"username": commenter_username, "text": new_comment})
      st.session_state[clear_flag_key] = True

    def _cancel_comment():
      st.session_state[clear_flag_key] = True
      st.session_state[show_comments_key] = False

    def _toggle_comments():
      st.session_state[show_comments_key] = not st.session_state[show_comments_key]

    st.markdown(
      """
      <style>
        div[data-testid="stButton"] > button {
          border: 1px solid #ccd6dd;
          border-radius: 8px;
        }
      </style>
      """,
      unsafe_allow_html=True,
    )

    controls_col1, controls_col2 = st.columns(2)
    with controls_col1:
      st.button(f"❤️ {likes} Likes", key=f"like_{post_id}", use_container_width=True)
    with controls_col2:
      st.button(
        f"💬 {len(st.session_state[comments_key])} Comments",
        key=f"toggle_comments_{post_id}",
        use_container_width=True,
        on_click=_toggle_comments,
      )

    if st.session_state[show_comments_key]:
      st.markdown("**Comments**")
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
          key=f"post_{post_id}",
          use_container_width=True,
          on_click=_post_comment,
        )

      with action_col2:
        st.button(
          "Cancel",
          key=f"cancel_{post_id}",
          use_container_width=True,
          on_click=_cancel_comment,
        )

      st.caption("Previous comments")
      if st.session_state[comments_key]:
        for old_comment in st.session_state[comments_key]:
          if isinstance(old_comment, dict):
            old_comment_username = old_comment.get("username", "User")
            old_comment_text = old_comment.get("text", "")
            st.markdown(f"- {old_comment_username}: {old_comment_text}")
          else:
            st.markdown(f"- User: {old_comment}")
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
    # for r=45, circumference is ~283
    offset = 283 - (283 * percent / 100)

   
    html_content = f"""
    <style>
      .activity-card {{
        border: 1px solid #e1e8ed;
        border-radius: 10px;
        padding: 20px;
        margin: 20px auto;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
        max-width: 600px;
        background-color: #fff;
        display: flex;
        align-items: center;
        gap: 30px;
      }}
      .ring-container {{
        position: relative;
        width: 120px;
        height: 120px;
      }}
      .ring-svg {{
        transform: rotate(-90deg);
      }}
      .ring-bg {{
        fill: none;
        stroke: #f5f8fa;
        stroke-width: 10;
      }}
      .ring-progress {{
        fill: none;
        stroke: #fa114f; /* Apple-style Move Red */
        stroke-width: 10;
        stroke-linecap: round;
        transition: stroke-dashoffset 0.5s ease;
      }}
      .percent-text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-weight: bold;
        font-size: 1.2em;
        color: #14171a;
      }}
      .info-container {{
        flex: 1;
      }}
      .stat-label {{
        color: #657786;
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }}
      .stat-value {{
        font-size: 1.8em;
        font-weight: 800;
        color: #14171a;
        margin: 5px 0;
      }}
    </style>

    <div class="activity-card">
      <div class="ring-container">
        <svg class="ring-svg" width="120" height="120">
          <circle class="ring-bg" cx="60" cy="60" r="45"></circle>
          <circle class="ring-progress" cx="60" cy="60" r="45" 
                  style="stroke-dasharray: 283; stroke-dashoffset: {offset};"></circle>
        </svg>
        <div class="percent-text">{percent}%</div>
      </div>
      
    <div class="info-container">
    <div style="margin-bottom: 12px;">
        <span class="stat-label">Total Workouts</span>
        <div style="font-size: 1.2em; font-weight: 800; color: #14171a;">{total_workouts}</div>
    </div>

    <div style="margin-bottom: 12px;">
        <span class="stat-label">Time Spent</span>
        <div style="font-size: 1.2em; font-weight: 800; color: #1da1f2;">{time_val}</div>
    </div>

    <div>
        <span class="stat-label">Move Goal</span>
        <div class="stat-value" style="font-size: 1.5em; margin: 0;">{total_calories} <span style="font-size: 0.5em; color: #657786;">/ {calorie_goal} KCAL</span></div>
      </div>
    </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)


def display_recent_workouts(workouts_list):
    """Displays a list of recent workouts with key metrics in a table format.
    
    Args:
        workouts_list: A list of workout dictionaries containing workout details
                      such as date, exercise type, duration, and calories burned.
    """
    if not workouts_list or len(workouts_list) == 0:
        st.info("No recent workouts found. Start your fitness journey today!")
        return
    
    st.header("Recent Workouts")
    
    # Display workouts as a dataframe for easy viewing
    st.dataframe(workouts_list, use_container_width=True)
    
    # Display summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_workouts = len(workouts_list)
        st.metric("Total Workouts", total_workouts)
    
    with col2:
        # Sum duration if available
        total_duration = sum([w.get('duration', 0) for w in workouts_list])
        st.metric("Total Duration (min)", total_duration)
    
    with col3:
        # Sum calories if available
        total_calories = sum([w.get('calories_burned', 0) for w in workouts_list])
        st.metric("Total Calories", total_calories)


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
