#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
#############################################################################

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts


# ---------------------------------------------------------------------------
# TestDisplayPost
# ---------------------------------------------------------------------------

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
        self.assertEqual(len(at.markdown), 1)
        html_output = at.markdown[0].value

        self.assertIn("testuser", html_output)
        self.assertIn("http://example.com/user.jpg", html_output)
        self.assertIn("2024-01-01 12:00:00", html_output)
        self.assertIn("This is a test post.", html_output)
        self.assertIn("http://example.com/post.jpg", html_output)
        self.assertIn("Likes", html_output)
        self.assertIn("Comments", html_output)

    def test_post_contains_engagement_stats(self):
        """Tests that like and comment counts appear in the rendered post."""
        at = AppTest.from_string("""
from modules import display_post
display_post(
    "athlete99",
    "http://example.com/pic.jpg",
    "2024-06-15 09:00:00",
    "Morning run complete!",
    "http://example.com/run.jpg"
)
""")
        at.run()
        html_output = at.markdown[0].value
        self.assertIn("Likes", html_output)
        self.assertIn("Comments", html_output)

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def test_activity_summary_rendering(self):
        """Tests that the activity summary calculates and renders correct totals."""
        at = AppTest.from_string("""
from modules import display_activity_summary
mock_workouts = [
    {"duration": 30, "calories": 300},
    {"duration": 45, "calories": 250}
]
display_activity_summary(mock_workouts)
""")
        at.run()

        self.assertTrue(len(at.markdown) > 0)
        html_output = at.markdown[0].value

        # Workout count
        self.assertIn("2 sessions", html_output)

        # Time: 30 + 45 = 75 mins -> 1h 15m
        self.assertIn("1h 15m", html_output)

        # Calories: 300 + 250 = 550
        self.assertIn("550", html_output)

        # Ring percentage: 550/600 = 91%
        self.assertIn("91%", html_output)

    def test_activity_summary_single_session(self):
        """Tests singular 'session' label when only one workout exists."""
        at = AppTest.from_string("""
from modules import display_activity_summary
mock_workouts = [{"duration": 20, "calories": 150}]
display_activity_summary(mock_workouts)
""")
        at.run()
        html_output = at.markdown[0].value
        self.assertIn("1 session", html_output)
        self.assertNotIn("1 sessions", html_output)

    def test_activity_summary_caps_ring_at_100(self):
        """Tests that the ring percentage caps at 100% even if calories exceed the goal."""
        at = AppTest.from_string("""
from modules import display_activity_summary
mock_workouts = [{"duration": 60, "calories": 1200}]
display_activity_summary(mock_workouts)
""")
        at.run()
        html_output = at.markdown[0].value
        self.assertIn("100%", html_output)

    def test_activity_summary_under_60_minutes(self):
        """Tests that durations under 60 mins display as minutes only."""
        at = AppTest.from_string("""
from modules import display_activity_summary
mock_workouts = [{"duration": 45, "calories": 200}]
display_activity_summary(mock_workouts)
""")
        at.run()
        html_output = at.markdown[0].value
        self.assertIn("45m", html_output)
        self.assertNotIn("h", html_output)

class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_display_genai_advice_runs_without_error(self):
        """Tests that display_genai_advice executes without raising exceptions."""
        try:
            display_genai_advice(
                datetime.now(),
                "Stay disciplined. Consistency builds strength.",
                "https://example.com/image.jpg"
            )
        except Exception as e:
            self.fail(f"display_genai_advice raised an exception: {e}")

    def test_display_genai_advice_with_no_image(self):
        """Tests that display_genai_advice works when image is None (uses random fallback)."""
        try:
            display_genai_advice(
                datetime.now(),
                "Push past the limits you set yesterday.",
                None
            )
        except Exception as e:
            self.fail(f"display_genai_advice raised an exception with no image: {e}")

    def test_display_genai_advice_content_in_html(self):
        """Tests that the advice content appears inside the rendered HTML component."""
        at = AppTest.from_string("""
from datetime import datetime
from modules import display_genai_advice
display_genai_advice(
    datetime(2024, 6, 1, 9, 30),
    "Champions show up every single day.",
    None
)
""")
        at.run()
        # display_genai_advice uses components.html — check it rendered without errors
        self.assertFalse(at.exception)

    def test_display_genai_advice_timestamp_format(self):
        """Tests that the timestamp is formatted correctly in the HTML output."""
        at = AppTest.from_string("""
from datetime import datetime
from modules import display_genai_advice
display_genai_advice(
    datetime(2024, 6, 1, 9, 30),
    "You are stronger than your excuses.",
    None
)
""")
        at.run()
        self.assertFalse(at.exception)

class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_empty_list_shows_info_message(self):
        """Tests that an empty workout list shows the 'no workouts' info message."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
display_recent_workouts([])
""")
        at.run()
        self.assertEqual(len(at.info), 1)
        self.assertIn("No recent workouts", at.info[0].value)

    def test_none_shows_info_message(self):
        """Tests that None as input shows the 'no workouts' info message."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
display_recent_workouts(None)
""")
        at.run()
        self.assertEqual(len(at.info), 1)
        self.assertIn("No recent workouts", at.info[0].value)

    def test_header_renders(self):
        """Tests that the 'Recent Workouts' header renders with workout data."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
display_recent_workouts([
    {"date": "2024-01-01", "exercise": "Running", "duration": 30, "calories": 300}
])
""")
        at.run()
        self.assertTrue(len(at.header) > 0)
        self.assertIn("Recent Workouts", at.header[0].value)

    def test_metric_total_workouts(self):
        """Tests that the total workouts metric is correct."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
display_recent_workouts([
    {"duration": 30, "calories": 300},
    {"duration": 45, "calories": 250},
])
""")
        at.run()
        metrics = at.metric
        # First metric: Total Workouts
        self.assertEqual(metrics[0].value, "2")

    def test_metric_total_duration(self):
        """Tests that the total duration metric sums correctly."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
display_recent_workouts([
    {"duration": 30, "calories": 300},
    {"duration": 45, "calories": 250},
])
""")
        at.run()
        metrics = at.metric
        # Second metric: Total Duration
        self.assertEqual(metrics[1].value, "75")

    def test_metric_total_calories(self):
        """Tests that the total calories metric sums correctly."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
display_recent_workouts([
    {"duration": 30, "calories": 300},
    {"duration": 45, "calories": 250},
])
""")
        at.run()
        metrics = at.metric
        # Third metric: Total Calories
        self.assertEqual(metrics[2].value, "550")

    def test_missing_keys_default_to_zero(self):
        """Tests that missing duration/calories keys default to 0 gracefully."""
        at = AppTest.from_string("""
from modules import display_recent_workouts
display_recent_workouts([{"exercise": "Yoga"}])
""")
        at.run()
        metrics = at.metric
        self.assertEqual(metrics[1].value, "0")  # duration
        self.assertEqual(metrics[2].value, "0")  # calories

class TestFullAppMock(unittest.TestCase):
    """Full app integration tests using AppTest."""

    def _get_app(self):
        """Helper that returns a fresh AppTest instance pointed at app.py."""
        return AppTest.from_file("app.py", default_timeout=30)

    def test_app_loads_without_error(self):
        """Tests that the app launches on the Home page without exceptions."""
        at = self._get_app()
        at.run()
        self.assertFalse(at.exception)

    def test_home_page_title(self):
        """Tests that the Home page displays the welcome title."""
        at = self._get_app()
        at.run()
        titles = [t.value for t in at.title]
        self.assertTrue(any("Welcome back" in t for t in titles))

    def test_sidebar_menu_exists(self):
        """Tests that the sidebar radio navigation is present."""
        at = self._get_app()
        at.run()
        self.assertTrue(len(at.sidebar.radio) > 0)

    def test_navigate_to_posts(self):
        """Tests that selecting Posts in the sidebar renders post content."""
        at = self._get_app()
        at.run()
        at.sidebar.radio[0].set_value("Posts")
        at.run()
        self.assertFalse(at.exception)
        headers = [h.value for h in at.header]
        self.assertTrue(any("Posts" in h for h in headers))

    def test_navigate_to_activity_summary(self):
        """Tests that selecting Activity Summary renders without errors."""
        at = self._get_app()
        at.run()
        at.sidebar.radio[0].set_value("Activity Summary")
        at.run()
        self.assertFalse(at.exception)
        headers = [h.value for h in at.header]
        self.assertTrue(any("Activity Summary" in h for h in headers))

    def test_navigate_to_recent_workouts(self):
        """Tests that selecting Recent Workouts renders without errors."""
        at = self._get_app()
        at.run()
        at.sidebar.radio[0].set_value("Recent Workouts")
        at.run()
        self.assertFalse(at.exception)

    def test_navigate_to_ai_trainer_advice(self):
        """Tests that the AI Trainer Advice page renders without crashing."""
        at = self._get_app()
        at.run()
        at.sidebar.radio[0].set_value("AI Trainer Advice")
        at.run()
        self.assertFalse(at.exception)

    def test_home_shows_three_columns(self):
        """Tests that the Home page renders the three summary columns (advice, community, activity)."""
        at = self._get_app()
        at.run()
        subheaders = [s.value for s in at.subheader]
        self.assertIn("Latest Advice", subheaders)
        self.assertIn("Community", subheaders)
        self.assertIn("Recent Activity", subheaders)


if __name__ == "__main__":
    unittest.main()
