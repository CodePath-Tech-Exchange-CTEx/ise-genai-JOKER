import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from data_fetcher import (
    get_user_sensor_data, 
    get_user_posts, 
    get_user_workouts, 
    get_user_profile,
    # get_genai_advice
)

class TestDataFetcher(unittest.TestCase):

    @patch('data_fetcher.client')
    def test_get_user_sensor_data_structure(self, mock_client):
        """Tests that sensor data returns the correct keys and joined units."""
        mock_row = {
            'sensor_type': 'Heart Rate',
            'timestamp': datetime(2026, 3, 29, 8, 15, 0),
            'data': 145.0,
            'units': 'bpm'
        }
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job

        results = get_user_sensor_data('user1', 'w_001')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['sensor_type'], 'Heart Rate')
        self.assertEqual(results[0]['units'], 'bpm')

    @patch('data_fetcher.client')
    def test_get_user_posts_mapping(self, mock_client):
        """Tests that posts are mapped correctly for the display_post module."""
        mock_row = {
            'post_id': 'p_101',
            'user_id': 'user1',
            'timestamp': datetime(2026, 3, 29, 10, 0, 0),
            'image': 'http://example.com/fit.jpg',
            'content': 'Morning run!'
        }
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job

        results = get_user_posts('user1')
        
        self.assertEqual(results[0]['post_id'], 'p_101')
        self.assertTrue('content' in results[0])

    @patch('data_fetcher.client')
    def test_get_user_workouts_schema(self, mock_client):
        """Tests the full workout schema matches the UI requirements."""
        mock_row = {
            'workout_id': 'w_001',
            'start_timestamp': datetime(2026, 3, 29, 8, 0, 0),
            'end_timestamp': datetime(2026, 3, 29, 9, 0, 0),
            'start_lat_lng_lat': 34.05,
            'start_lat_lng_lng': -118.24,
            'distance': 5.0,
            'steps': 7000,
            'calories_burned': 450.0
        }
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job

        results = get_user_workouts('user1')
        
        self.assertEqual(results[0]['duration'], 60)
        self.assertEqual(results[0]['calories_burned'], 450.0)

    @patch('data_fetcher.client')
    def test_get_user_profile_full_mapping(self, mock_client):
        """Tests that user profile correctly merges user data and friends list."""

        user_row = {
            'full_name': 'Remi',
            'username': 'remi_the_rems',
            'date_of_birth': datetime(1990, 1, 1),
            'profile_image': 'http://example.com/remi.jpg'
        }
        
        friend_rows = [{'UserId2': 'user2'}, {'UserId2': 'user3'}]
        
        mock_user_job = MagicMock()
        mock_user_job.result.return_value = [user_row]
        
        mock_friends_job = MagicMock()
        mock_friends_job.result.return_value = friend_rows
        
        mock_client.query.side_effect = [mock_user_job, mock_friends_job]

        result = get_user_profile('user1')

        self.assertIsNotNone(result)
        self.assertEqual(result['full_name'], 'Remi')
        self.assertEqual(result['username'], 'remi_the_rems')
        
        self.assertEqual(len(result['friends']), 2)
        self.assertIn('user2', result['friends'])
        self.assertIn('user3', result['friends'])

    @patch('data_fetcher.client')
    def test_get_user_workouts_duration_calculation(self, mock_client):
        """Tests that duration is correctly calculated from timestamps."""
        # 1. Setup Mock Row Data
        start = datetime(2024, 7, 29, 7, 0, 0)
        end = datetime(2024, 7, 29, 8, 0, 0) # Exactly 60 minutes
        
        mock_row = {
            'workout_id': 'w1',
            'start_timestamp': start,
            'end_timestamp': end,
            'start_lat_lng_lat': 37.77,
            'start_lat_lng_lng': -122.41,
            'distance': 5.0,
            'steps': 8000,
            'calories_burned': 400
        }

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job

        results = get_user_workouts('user1')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['duration'], 60)
        self.assertEqual(results[0]['workout_id'], 'w1')

    @patch('data_fetcher.client')
    def test_get_user_profile_none(self, mock_client):
        """Tests that None is returned if no user is found."""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job

        result = get_user_profile('non_existent_user')
        self.assertIsNone(result)

    @patch('data_fetcher.client')
    def test_get_user_workouts_missing_end_time(self, mock_client):
        """Tests that workouts with missing end times don't crash the duration calc."""
        mock_row = {
            'workout_id': 'w2',
            'start_timestamp': datetime(2024, 7, 29, 7, 0, 0),
            'end_timestamp': None,
            'distance': 2.0
        }
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job

        results = get_user_workouts('user1')
        
        self.assertNotIn('duration', results[0])
        self.assertEqual(results[0]['distance'], 2.0)


    @patch('data_fetcher.client')
    def test_get_user_workouts_empty(self, mock_client):
        """Tests that an empty workout list is returned gracefully."""
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [] 
        mock_client.query.return_value = mock_query_job

        results = get_user_workouts('new_user_with_no_history')
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

    @patch('data_fetcher.client')
    def test_get_user_profile_no_friends(self, mock_client):
        """Tests that a user profile is returned correctly even with zero friends."""
        user_row = {
            'full_name': 'Solo Traveler',
            'username': 'solo',
            'date_of_birth': datetime(1995, 1, 1),
            'profile_image': 'http://example.com/p.jpg'
        }
        
        mock_query_job_user = MagicMock()
        mock_query_job_user.result.return_value = [user_row]
        
        mock_query_job_friends = MagicMock()
        mock_query_job_friends.result.return_value = []
        
        # side_effect allows the mock to return different things for the 1st vs 2nd call
        mock_client.query.side_effect = [mock_query_job_user, mock_query_job_friends]

        result = get_user_profile('user_with_no_friends')

        self.assertIsNotNone(result)
        self.assertEqual(result['full_name'], 'Solo Traveler')
        self.assertEqual(result['friends'], [])   

if __name__ == "__main__":
    unittest.main()