"""Activity page UI with recent workouts, summary, and share-to-community."""

import streamlit as st

from data_fetcher import create_user_post, get_user_profile, get_user_workouts
from modules import display_post, display_recent_workouts


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
    return f'Look at this, I walked {steps} steps today!'


def display_activity_page(user_id):
    """Display a user's activity page and allow sharing a stat as a post."""
    st.header('My Activity')

    profile = get_user_profile(user_id)
    workouts = get_user_workouts(user_id)

    if not workouts:
        st.info('No workouts found yet. Log a workout to see your activity here.')
        return

    st.subheader('Activity Summary')
    total_workouts, total_steps, total_calories = _build_activity_summary(workouts)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Workouts', total_workouts)
    with col2:
        st.metric('Total Steps', total_steps)
    with col3:
        st.metric('Total Calories', total_calories)

    st.subheader('Recent 3 Workouts')
    display_recent_workouts(workouts[:3])

    st.divider()
    st.subheader('Share With Community')
    st.caption('Share one simple stat as a post from your account.')

    if st.button('Share My Steps', type='primary'):
        post_content = _build_share_content(workouts)
        created_post = create_user_post(user_id, post_content)
        st.success('Your post was shared to the community.')

        display_post(
            username=profile.get('username', user_id),
            user_image=profile.get('profile_image', ''),
            timestamp=created_post['timestamp'],
            content=created_post['content'],
            post_image=created_post.get('image', ''),
        )


if __name__ == '__main__':
    display_activity_page('user1')
