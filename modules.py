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


def display_post(username, user_image, timestamp, content, post_image):
    """Displays a post with user information, content, and engagement stats.

    Args:
        username: The username of the post's author.
        user_image: The URL for the user's profile image.
        timestamp: The time the post was made.
        content: The text content of the post.
        post_image: The URL for the main image of the post.
    """
    likes = random.randint(0, 1000)
    comments = random.randint(0, 500)

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
      .footer-button {{
        display: flex;
        align-items: center;
        gap: 5px;
        background: none;
        border: none;
        color: #657786;
        cursor: pointer;
        font-size: 1em;
        padding: 5px;
      }}
      .footer-button:hover {{
        color: #1da1f2; /* A nice blue for hover effect */
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
        <div>
          <button class="footer-button"><span>&#10084;&#65039;</span> {likes} Likes</button>
          <button class="footer-button"><span>&#128172;</span> {comments} Comments</button>
        </div>
      </div>
    </div>
    """
    st.markdown(post_html, unsafe_allow_html=True)


def display_activity_summary(workouts_list):
    """Displays the total metrics of the user's workout (number of workouts, total time spent, total calories burned)
    
    Arg:
        workouts_list: list of workouts.
    """
    
    total_workouts = str(len(workouts_list)) + ' sessions' if len(workouts_list) > 1 else str(len(workouts_list)) + ' session'
    total_minutes = sum(w.get('duration', 0) for w in workouts_list)
    time_val = f"{total_minutes // 60}h {total_minutes % 60}m" if total_minutes > 60 else f"{total_minutes}m"
    total_calories = sum(w.get('calories', 0) for w in workouts_list)
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
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    st.divider()
    
    st.subheader("Your AI Workout Motivation")

    formatted_time = timestamp.strftime("%B %d, %Y at %I:%M %p")
    st.caption(f"Generated on {formatted_time}")

    if image:
        st.image(image, use_column_width=True)

    st.markdown(f"AI Says:\n{content}")

    st.divider()
