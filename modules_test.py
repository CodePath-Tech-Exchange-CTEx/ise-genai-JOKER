import unittest
import sys
import types
from datetime import datetime
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from modules import display_activity_summary
from pages import display_posts_page, display_genai_advice, display_recent_workouts


MOCK_PROFILE = {
    'full_name': 'Remi',
    'username': 'remi_the_rems',
    'date_of_birth': '1990-01-01',
    'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
    'friends': ['user2', 'user3'],
}

MOCK_POSTS = [{
    'user_id': 'user1',
    'post_id': 'post1',
    'timestamp': '2024-01-01 00:00:00',
    'content': 'Had a great workout today!',
    'image': 'image_url',
}]

MOCK_WORKOUTS = [
    {
        'workout_id': 'workout0',
        'start_timestamp': '2024-01-01 00:00:00',
        'end_timestamp': '2024-01-01 00:30:00',
        'start_lat_lng': (1.5, 4.5),
        'end_lat_lng': (1.6, 4.6),
        'distance': 5.0,
        'steps': 6000,
        'calories_burned': 300,
    },
    {
        'workout_id': 'workout1',
        'start_timestamp': '2024-01-02 00:00:00',
        'end_timestamp': '2024-01-02 00:45:00',
        'start_lat_lng': (1.2, 4.2),
        'end_lat_lng': (1.3, 4.3),
        'distance': 7.0,
        'steps': 9000,
        'calories_burned': 250,
    },
]

MOCK_ADVICE = {
    'advice_id': 'advice1',
    'timestamp': '2024-01-01 00:00:00',
    'content': 'You are doing great! Keep up the good work.',
    'image': None,
}

MOCK_SENSOR = [
    {'sensor_type': 'heart_rate', 'timestamp': '2024-01-01 00:01:00', 'data': 75.0},
]

# Simulates a successfully authenticated user
MOCK_AUTH_USER = {
    'user_id': 'user1',
    'username': 'remi_the_rems',
}


class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_post_rendering(self):
        """Tests that the post renders with the correct information."""
        at = AppTest.from_string("""
from pages import display_posts_page
display_posts_page(
    "testuser",
    "http://example.com/user.jpg",
    "2024-01-01 12:00:00",
    "This is a test post.",
    "http://example.com/post.jpg"
)
""")
        at.run()
        self.assertFalse(at.exception)
        self.assertGreaterEqual(len(at.markdown), 2)
        html_output = at.markdown[0].value
        self.assertIn("testuser", html_output)
        self.assertIn("This is a test post.", html_output)
        
        # We moved Likes and Comments to the interactive buttons, so we check the buttons instead!
        button_labels = [button.label for button in at.button]
        self.assertTrue(any("Like" in label for label in button_labels))
        self.assertTrue(any("Comment" in label for label in button_labels))

    def test_post_with_mock_data_fetcher_post(self):
        """Tests display_post using data matching get_user_posts() return format."""
        post = MOCK_POSTS[0]
        at = AppTest.from_string(f"""
from pages import display_posts_page
display_posts_page(
    "remi_the_rems",
    "http://example.com/pic.jpg",
    "{post['timestamp']}",
    "{post['content']}",
    "{post['image']}"
)
""")
        at.run()
        self.assertFalse(at.exception)
        html_output = at.markdown[0].value
        self.assertIn("remi_the_rems", html_output)
        self.assertIn(post['content'], html_output)

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function.
    
    Uses mocked workout data matching the exact return format of
    data_fetcher.get_user_workouts().
    """

    def test_activity_summary_renders_without_error(self):
        """Tests that the summary renders without errors using real data format."""
        at = AppTest.from_string("""
from modules import display_activity_summary
mock_workouts = [
    {
        'workout_id': 'workout0',
        'start_timestamp': '2024-01-01 00:00:00',
        'end_timestamp': '2024-01-01 00:30:00',
        'calories_burned': 300,
        'steps': 6000,
        'distance': 5.0,
    },
    {
        'workout_id': 'workout1',
        'start_timestamp': '2024-01-02 00:00:00',
        'end_timestamp': '2024-01-02 00:45:00',
        'calories_burned': 250,
        'steps': 9000,
        'distance': 7.0,
    },
]
display_activity_summary(mock_workouts)
""")
        at.run()
        self.assertFalse(at.exception)
        self.assertTrue(len(at.markdown) > 0)

    def test_activity_summary_single_session_label(self):
        """Tests singular session label with one workout."""
        at = AppTest.from_string("""
from modules import display_activity_summary
mock_workouts = [{
    'workout_id': 'workout0',
    'calories_burned': 150,
    'steps': 3000,
    'distance': 2.0,
}]
display_activity_summary(mock_workouts)
""")
        at.run()
        self.assertFalse(at.exception)
        html_output = at.markdown[0].value
        self.assertIn("1 session", html_output)
        self.assertNotIn("1 sessions", html_output)

class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function.
    
    Uses mocked advice matching the exact return format of
    data_fetcher.get_genai_advice().
    """

    def test_display_genai_advice_runs_without_error(self):
        """Tests that display_genai_advice runs using real data format."""
        try:
            display_genai_advice(
                datetime.now(),
                MOCK_ADVICE['content'],
                MOCK_ADVICE['image'],
            )
        except Exception as e:
            self.fail(f"display_genai_advice raised an exception: {e}")

    def test_display_genai_advice_no_exception_in_apptest(self):
        """Tests that display_genai_advice renders without errors in AppTest."""
        at = AppTest.from_string("""
from datetime import datetime
from pages import display_genai_advice
display_genai_advice(
    datetime(2024, 6, 1, 9, 30),
    "You are doing great! Keep up the good work.",
    None
)
""")
        at.run()
        self.assertFalse(at.exception)

class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function.
    
    Uses mocked workout data matching the exact return format of
    data_fetcher.get_user_workouts().
    """

    def test_empty_list_shows_info_message(self):
        """Tests that an empty list shows the no workouts message."""
        at = AppTest.from_string("""
from pages import display_recent_workouts
display_recent_workouts([])
""")
        at.run()
        self.assertEqual(len(at.info), 1)
        self.assertIn("No recent workouts", at.info[0].value)

    def test_none_shows_info_message(self):
        """Tests that None shows the no workouts message."""
        at = AppTest.from_string("""
from pages import display_recent_workouts
display_recent_workouts(None)
""")
        at.run()
        self.assertEqual(len(at.info), 1)
        self.assertIn("No recent workouts", at.info[0].value)

    def test_workouts_render_without_error(self):
        """Tests that workouts in the real data format render without errors."""
        at = AppTest.from_string("""
from pages import display_recent_workouts
mock_workouts = [
    {
        'workout_id': 'workout0',
        'start_timestamp': '2024-01-01 00:00:00',
        'end_timestamp': '2024-01-01 00:30:00',
        'distance': 5.0,
        'steps': 6000,
        'calories_burned': 300,
    },
    {
        'workout_id': 'workout1',
        'start_timestamp': '2024-01-02 00:00:00',
        'end_timestamp': '2024-01-02 00:45:00',
        'distance': 7.0,
        'steps': 9000,
        'calories_burned': 250,
    },
]
display_recent_workouts(mock_workouts)
""")
        at.run()
        self.assertFalse(at.exception)
        
        self.assertTrue(len(at.markdown) > 0)
        
        # Combine all markdown elements so we capture the header AND the cards
        all_html_output = "".join([m.value for m in at.markdown])
        
        # Verify our mock data actually made it into the HTML
        self.assertIn("6,000", all_html_output)

class TestFullAppMock(unittest.TestCase):
    """Full app integration tests with data_fetcher and auth fully mocked."""

    def _run_with_mocks(self, page=None):
        with patch("data_fetcher.get_user_profile", return_value=MOCK_PROFILE), \
            patch("data_fetcher.get_user_posts", return_value=MOCK_POSTS), \
            patch("data_fetcher.get_user_workouts", return_value=MOCK_WORKOUTS), \
            patch("data_fetcher.get_genai_advice", return_value=MOCK_ADVICE), \
            patch("data_fetcher.get_user_sensor_data", return_value=MOCK_SENSOR), \
            patch("data_fetcher.authenticate_user", return_value=MOCK_AUTH_USER), \
            patch("data_fetcher.get_people_you_may_know", return_value=[]):
                at = AppTest.from_file("app.py", default_timeout=30)
                at.session_state["authenticated"] = True
                at.session_state["user_id"] = "user1"
                at.session_state["username"] = "remi_the_rems"
                at.run()
                if page:
                    at.sidebar.radio[0].set_value(page)
                    at.run()
        return at

    def test_app_loads_without_error(self):
        at = self._run_with_mocks()
        self.assertFalse(at.exception)

    def test_sidebar_menu_exists(self):
        at = self._run_with_mocks()
        self.assertTrue(len(at.sidebar.radio) > 0)

    def test_navigate_to_posts(self):
        at = self._run_with_mocks(page="Posts")
        self.assertFalse(at.exception)

    def test_navigate_to_recent_workouts(self):
        at = self._run_with_mocks(page="Recent Workouts")
        self.assertFalse(at.exception)

    def test_navigate_to_ai_trainer_advice(self):
        at = self._run_with_mocks(page="AI Trainer Advice")
        self.assertFalse(at.exception)

class TestIndividualPages(unittest.TestCase):
    """Tests the individual page functions in the pages directory."""

    def test_profile_page_renders(self):
        """Tests that the Profile page renders correctly in View Mode."""
        # Use the context manager to force the patch exactly when the test runs
        with patch("pages.profile.get_user_profile", return_value=MOCK_PROFILE):
            at = AppTest.from_string("""
import streamlit as st
from pages import display_profile_page
display_profile_page('user1')
""")
            at.run()
            self.assertFalse(at.exception)
            
            html_output = "".join([m.value for m in at.markdown])
            self.assertIn("Profile", html_output)
            self.assertIn(MOCK_PROFILE['full_name'], html_output)
            self.assertIn(MOCK_PROFILE['username'], html_output)

    def test_community_page_renders(self):
        """Tests that the Community page renders the feed correctly."""
    
        MOCK_FEED = [{
            'post_id': 'post1',
            'username': 'best_friend_99',
            'user_image': 'http://example.com/pic.jpg',
            'timestamp': '2024-01-01 00:00:00',
            'content': 'Had a great workout today!',
            'post_image': '',
            'likes': 0,
            'comments': []
        }]

        with patch("pages.community.get_user_profile", return_value=MOCK_PROFILE), \
             patch("pages.community.get_friend_feed", return_value=MOCK_FEED), \
             patch("pages.community.get_genai_advice", return_value=MOCK_ADVICE):
            
            at = AppTest.from_string("""
import streamlit as st
from pages import display_community_page
display_community_page('user1')
""")
            at.run()
            
            if at.exception:
                print("\n COMMUNITY PAGE CRASHED:", at.exception[0].message, "\n")
                
            self.assertFalse(at.exception)
            
            html_output = "".join([m.value for m in at.markdown])
            
            self.assertIn(MOCK_FEED[0]['content'], html_output)

    def test_activity_page_renders(self):
        """Tests that the Activity page renders the summary and recent workouts."""

        with patch("pages.activity.get_user_profile", return_value=MOCK_PROFILE), \
             patch("pages.activity.get_user_workouts", return_value=MOCK_WORKOUTS):
             
            at = AppTest.from_string("""
import streamlit as st
from pages import display_activity_page
display_activity_page('user1')
""")
            at.run()
            
            if at.exception:
                print("\n ACTIVITY PAGE CRASHED:", at.exception[0].message, "\n")
                
            self.assertFalse(at.exception)
            
            html_output = "".join([m.value for m in at.markdown])
            self.assertIn("My Activity", html_output)
            self.assertIn("Total Workouts", html_output)
            self.assertIn("6,000", html_output)


if __name__ == "__main__":
    unittest.main()
