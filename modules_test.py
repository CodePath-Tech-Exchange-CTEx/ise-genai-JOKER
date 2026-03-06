#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from datetime import datetime
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_post_rendering(self):
        """Tests that the post renders with the correct information."""
        # Instead of from_function, we'll run the function inside a string
        # that looks like a small Streamlit script. This is more robust.
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
        # Check if the html component is rendered
        self.assertEqual(len(at.markdown), 1)
        html_output = at.markdown[0].value

        # Check for key pieces of information in the rendered HTML
        self.assertIn("testuser", html_output)
        self.assertIn("http://example.com/user.jpg", html_output)
        self.assertIn("2024-01-01 12:00:00", html_output)
        self.assertIn("This is a test post.", html_output)
        self.assertIn("http://example.com/post.jpg", html_output)
        self.assertIn("Likes", html_output)
        self.assertIn("Comments", html_output)


class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def test_activity_summary_rendering(self):
        """Tests that the activity summary calculates and renders correct totals."""
        at = AppTest.from_string("""
from modules import display_activity_summary
# Mock data to parse
mock_workouts = [
    {"duration": 30, "calories": 300},
    {"duration": 45, "calories": 250}
]
display_activity_summary(mock_workouts)
""")
        at.run()
        
        # The summary uses st.markdown for the HTML card
        self.assertTrue(len(at.markdown) > 0)
        html_output = at.markdown[0].value

        # 1. Test Workout Count (length of list)
        self.assertIn("2 sessions", html_output)

        # 2. Test Time Calculation (30 + 45 = 75 mins -> 1h 15m)
        self.assertIn("1h 15m", html_output)

        # 3. Test Calorie Calculation (300 + 250 = 550)
        self.assertIn("550", html_output)

        # 4. Test Progress Ring Percentage (550 / 600 goal approx 91%)
        self.assertIn("91%", html_output)


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_display_genai_advice_runs(self):
        """Test that display_genai_advice executes without errors."""
        try:
            display_genai_advice(
                datetime.now(),
                "Stay disciplined. Consistency builds strength.",
                "https://example.com/image.jpg"
            )
        except Exception as e:
            self.fail(f"display_genai_advice raised an exception: {e}")


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
