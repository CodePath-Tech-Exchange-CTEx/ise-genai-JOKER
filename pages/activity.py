"""Activity page UI with recent workouts, summary, and share-to-community."""

import streamlit as st
from data_fetcher import (
    append_post_comment,
    create_user_post,
    get_user_profile,
    get_user_workouts,
    increment_post_likes,
)
from pages import display_posts_page, display_recent_workouts
from modules import display_activity_summary


def _build_activity_summary(workouts):
    """Return simple summary numbers from a workouts list."""
    total_workouts = len(workouts)
    total_steps = sum((w.get('steps') or 0) for w in workouts)
    total_calories = sum((w.get('calories_burned') or 0) for w in workouts)
    return total_workouts, int(total_steps), int(total_calories)


def _build_share_content(workouts):
    """Create a short share message from the latest workout."""
    if not workouts:
        return 'Look at this, I finished a workout today!'

    latest = workouts[0]
    steps = int(latest.get('steps') or 0)
    return f'Look at this, I walked {steps:,} steps today! 🔥'


def display_activity_page(user_id):
    """Display a user's activity page and allow sharing a stat as a post."""
    
    # Main Page Title (Keeping it massive)
    st.markdown("<h1 style='font-size: 3.5em; line-height: 1; margin-bottom: 30px;'>My Activity</h1>", unsafe_allow_html=True)

    profile = get_user_profile(user_id) or {}
    workouts = get_user_workouts(user_id) or []

    if not workouts:
        st.info('No workouts found yet. Log a workout to see your activity here.')
        return

    # ---------------------------------------------------------
    # HELPER FUNCTION: Sleek Headers with Gradient Divider
    # ---------------------------------------------------------
    def styled_header(title, subtitle):
        st.markdown(f"""
        <div style="margin-top: 20px; margin-bottom: 20px;">
            <h2 style="font-family: 'Bebas Neue', sans-serif; font-size: 2.2em; color: #ffffff; letter-spacing: 0.05em; margin: 0 0 10px 0; line-height: 1;">{title}</h2>
            <div style="width: 44px; height: 3px; background: linear-gradient(90deg, #fa114f, #ff6b35); border-radius: 2px; margin-bottom: 12px;"></div>
            <div style="font-family: 'DM Sans', sans-serif; color: #657786; font-size: 0.9em;">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)

    # 1. Activity Summary Section
    styled_header("Activity Summary", "A complete snapshot of your current progress.")
    display_activity_summary(workouts)

    st.markdown("<br>", unsafe_allow_html=True)

    total_workouts, total_steps, total_calories = _build_activity_summary(workouts)

    # Custom HTML for the 3 summary metrics
    summary_html = f"""
    <div style="display: flex; gap: 20px; margin-bottom: 50px;">
        <div style="flex: 1; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-family: 'DM Sans', sans-serif; font-size: 0.75em; color: #fa114f; text-transform: uppercase; letter-spacing: 0.1em; font-weight: bold; margin-bottom: 5px;">Total Workouts</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5em; color: #ffffff; line-height: 1;">{total_workouts}</div>
        </div>
        <div style="flex: 1; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-family: 'DM Sans', sans-serif; font-size: 0.75em; color: #fa114f; text-transform: uppercase; letter-spacing: 0.1em; font-weight: bold; margin-bottom: 5px;">Total Steps</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5em; color: #ffffff; line-height: 1;">{total_steps:,}</div>
        </div>
        <div style="flex: 1; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-family: 'DM Sans', sans-serif; font-size: 0.75em; color: #fa114f; text-transform: uppercase; letter-spacing: 0.1em; font-weight: bold; margin-bottom: 5px;">Calories Burned</div>
            <div style="font-family: 'Bebas Neue', sans-serif; font-size: 2.5em; color: #ffffff; line-height: 1;">{total_calories:,}</div>
        </div>
    </div>
    """
    st.markdown(summary_html, unsafe_allow_html=True)

    # 2. Recent Workouts Section
    styled_header("Recent Workouts", "Your latest logged workouts.")
    st.markdown("<br>", unsafe_allow_html=True)
    display_recent_workouts(workouts[:3])

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    
    # 3. Share Section
    styled_header("Share With Community", "Share a quick stat from your latest workout to your feed.")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button('Share My Latest Stats', type='primary', use_container_width=True):
        post_content = _build_share_content(workouts)
        created_post = create_user_post(user_id, post_content)
        st.success('Your post was shared to the community.')

        display_posts_page(
            username=profile.get('username', user_id),
            user_image=profile.get('profile_image', ''),
            timestamp=created_post['timestamp'],
            content=created_post['content'],
            post_image=created_post.get('image', ''),
            commenter_username=profile.get('username', user_id),
            post_id=created_post.get('post_id'),
            initial_likes=created_post.get('likes', 0),
            initial_comments=created_post.get('comments', []),
            on_like=increment_post_likes,
            on_comment=append_post_comment,
        )

if __name__ == '__main__':
    display_activity_page('user1')