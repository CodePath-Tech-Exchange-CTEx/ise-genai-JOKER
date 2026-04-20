import streamlit as st
from datetime import datetime

def display_posts_page(
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
