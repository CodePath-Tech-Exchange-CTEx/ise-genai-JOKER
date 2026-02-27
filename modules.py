#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

import random
import streamlit.components.v1 as components


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
    <script>
      // Simple script to resize the iframe to the height of the post
      const post = document.querySelector('.post');
      if (post) {{
        window.parent.postMessage({{
          'type': 'streamlit:setFrameHeight',
          'height': post.offsetHeight + 20  // Add a little extra padding
        }}, '*');
      }}
    </script>
    """
    components.html(post_html, height=600, scrolling=True)


def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass


def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
