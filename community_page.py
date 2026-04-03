"""Community page UI for friend posts and encouragement."""

from datetime import datetime

import streamlit as st

from data_fetcher import get_genai_advice, get_user_posts, get_user_profile
from modules import display_post


def _parse_timestamp(value):
    """Parse timestamp strings safely so posts can be sorted."""
    if not value:
        return datetime.min

    try:
        return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return datetime.min


def _get_friend_posts(user_id):
    """Fetch posts for all friends of a user."""
    user_profile = get_user_profile(user_id)
    friend_ids = user_profile.get('friends', [])

    posts = []
    for friend_id in friend_ids:
        friend_profile = get_user_profile(friend_id)
        friend_posts = get_user_posts(friend_id)

        for post in friend_posts:
            posts.append(
                {
                    'username': friend_profile.get('username', friend_id),
                    'user_image': friend_profile.get('profile_image', ''),
                    'timestamp': post.get('timestamp'),
                    'content': post.get('content', ''),
                    'post_image': post.get('image', ''),
                }
            )

    posts.sort(key=lambda post: _parse_timestamp(post.get('timestamp')), reverse=True)
    return posts[:10]


def display_community_page(user_id):
    """Display community home page: friend posts and one AI encouragement."""
    st.header('Community')

    advice = get_genai_advice(user_id)
    st.subheader('AI Advice and Encouragement')
    st.info(advice.get('content', 'Keep going. You are doing great.'))

    st.subheader('Latest Posts From Friends')
    friend_posts = _get_friend_posts(user_id)

    if not friend_posts:
        st.info('No friend posts found yet.')
        return

    for post in friend_posts:
        display_post(
            username=post['username'],
            user_image=post['user_image'],
            timestamp=post['timestamp'],
            content=post['content'],
            post_image=post['post_image'],
        )


if __name__ == '__main__':
    display_community_page('user1')