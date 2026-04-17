import unittest
import sys
import types
from datetime import datetime
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts


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
    {'sensor_type': 'accelerometer', 'timestamp': '2024-01-01 00:02:00', 'data': 12.3},
]


class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_post_rendering(self):
        """Tests that the post renders with the correct information."""
        at = AppTest.from_string("""
from modules import display_post
display_post(
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
        self.assertIn("Likes", html_output)
        button_labels = [button.label for button in at.button]
        self.assertTrue(any("Comments" in label for label in button_labels))

    def test_post_with_mock_data_fetcher_post(self):
        """Tests display_post using data matching get_user_posts() return format."""
        post = MOCK_POSTS[0]
        at = AppTest.from_string(f"""
from modules import display_post
display_post(
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
from modules import display_genai_advice
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
from modules import display_recent_workouts
display_recent_workouts([])
""")
        at.run()
        self.assertEqual(len(at.info), 1)
        self.assertIn("No recent workouts", at.info[0].value)

    def test_none_shows_info_message(self):
        """Tests that None shows the no workouts message."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
display_recent_workouts(None)
""")
        at.run()
        self.assertEqual(len(at.info), 1)
        self.assertIn("No recent workouts", at.info[0].value)

    def test_workouts_render_without_error(self):
        """Tests that workouts in the real data format render without errors."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
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
        self.assertTrue(len(at.metric) > 0)

class TestFullAppMock(unittest.TestCase):
    """Full app integration tests with data_fetcher fully mocked.
    
    All data_fetcher functions are patched to return controlled data
    matching the exact formats defined in data_fetcher.py, so tests
    run without needing any external database or credentials.
    """

    def _run_with_mocks(self, page=None):
        """Runs app.py with all data_fetcher functions mocked out."""
        mock_auth_user = {
            'user_id': 'user999999',
            'username': MOCK_PROFILE['username'],
            'full_name': MOCK_PROFILE['full_name'],
        }
        google_mod = types.ModuleType("google")
        cloud_mod = types.ModuleType("google.cloud")
        bigquery_mod = types.ModuleType("google.cloud.bigquery")
        generativeai_mod = types.ModuleType("google.generativeai")
        with patch.dict(
            sys.modules,
            {
                "google": google_mod,
                "google.cloud": cloud_mod,
                "google.cloud.bigquery": bigquery_mod,
                "google.generativeai": generativeai_mod,
            },
        ), patch("data_fetcher.get_user_profile", return_value=MOCK_PROFILE), \
            patch("data_fetcher.get_user_posts", return_value=MOCK_POSTS), \
            patch("data_fetcher.get_user_workouts", return_value=MOCK_WORKOUTS), \
            patch("data_fetcher.get_genai_advice", return_value=MOCK_ADVICE), \
            patch("data_fetcher.get_user_sensor_data", return_value=MOCK_SENSOR), \
            patch("data_fetcher.authenticate_user", return_value=mock_auth_user), \
            patch("data_fetcher.create_user_account", return_value=mock_auth_user):
            at = AppTest.from_file("app.py", default_timeout=30)
            at.run()
            # Authenticate through the login form so sidebar pages become available.
            at.text_input[0].set_value(MOCK_PROFILE['username'])
            at.text_input[1].set_value("test-password")
            at.button[0].click()
            at.run()
            if page:
                at.sidebar.radio[0].set_value(page)
                at.run()
        return at

    def test_app_loads_without_error(self):
        """Tests that the app loads on the Home page without exceptions."""
        at = self._run_with_mocks()
        self.assertFalse(at.exception)

    def test_sidebar_menu_exists(self):
        """Tests that the sidebar navigation is present."""
        at = self._run_with_mocks()
        self.assertTrue(len(at.sidebar.radio) > 0)

    def test_navigate_to_posts(self):
        """Tests that the Posts page renders without errors."""
        at = self._run_with_mocks(page="Posts")
        self.assertFalse(at.exception)

    def test_navigate_to_recent_workouts(self):
        """Tests that the Recent Workouts page renders without errors."""
        at = self._run_with_mocks(page="Recent Workouts")
        self.assertFalse(at.exception)

    def test_navigate_to_ai_trainer_advice(self):
        """Tests that the AI Trainer Advice page renders without errors."""
        at = self._run_with_mocks(page="AI Trainer Advice")
        self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()
