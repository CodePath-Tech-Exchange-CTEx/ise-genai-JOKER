#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_post_rendering(self):
        """Tests that the post renders with the correct information."""
        at = AppTest.from_function(
            display_post,
            args=(
                "testuser",
                "http://example.com/user.jpg",
                "2024-01-01 12:00:00",
                "This is a test post.",
                "http://example.com/post.jpg",
            ),
        )
        at.run()

        # Check if the html component is rendered
        self.assertEqual(len(at.html), 1)
        html_output = at.html[0].value

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

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
