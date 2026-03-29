#############################################################################
# data_fetcher.py
#
# BigQuery-backed data access layer for app.py.
#
# Required environment setup:
# - GOOGLE_APPLICATION_CREDENTIALS set to your service account JSON path
# - BIGQUERY_PROJECT_ID set to your GCP project id (optional if auto-detected)
# - BIGQUERY_DATASET defaults to "JOKER"
# - BIGQUERY_LOCATION defaults to "us-central1"
#############################################################################

import os
import random
import importlib
from datetime import datetime

try:
    from google.cloud import bigquery
except ImportError as exc:
    raise ImportError(
        'google-cloud-bigquery is required. Install with: pip install google-cloud-bigquery'
    ) from exc

try:
    genai = importlib.import_module('google.generativeai')
except ImportError:
    genai = None


# 1. Configuration using Environment Variables
BILLING_PROJECT_ID = os.getenv('BIGQUERY_BILLING_PROJECT_ID', 'juan-david-buitrago-fiu')
DATA_PROJECT_ID = os.getenv('BIGQUERY_PROJECT_ID', 'robert-hardy-hu')
DATASET_NAME = os.getenv('BIGQUERY_DATASET', 'JOKER')
LOCATION = os.getenv('BIGQUERY_LOCATION', 'US')

# Path to your Service Account JSON key (e.g., 'credentials.json')
# This should be set in your local .env file
KEY_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# 2. Updated Helper Functions
def _get_client():
    """
    Returns a client using the local JSON key if available, 
    otherwise falls back to default environment auth.
    """
    if KEY_PATH and os.path.exists(KEY_PATH):
        return bigquery.Client.from_service_account_json(
            KEY_PATH, 
            project=BILLING_PROJECT_ID, 
            location=LOCATION
        )
    
    # Fallback for when the code runs on a real GCP server (App Engine/Cloud Functions)
    return bigquery.Client(project=BILLING_PROJECT_ID, location=LOCATION)

def _qualified_table(table_name):
    return f'`{DATA_PROJECT_ID}.{DATASET_NAME}.{table_name}`'

def _query(sql, params=None):
    client = _get_client()
    job_config = bigquery.QueryJobConfig(query_parameters=params or [])
    # Location is required here because the dataset is in 'US'
    return client.query(sql, job_config=job_config, location=LOCATION).result()

def _format_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return str(value)


def get_user_sensor_data(user_id, workout_id):
    """Returns a list of timestamped sensor rows for a given workout."""
    sql = f"""
        SELECT
            COALESCE(st.Name, sd.SensorId) AS sensor_type,
            sd.Timestamp AS timestamp,
                        sd.SensorValue AS data,
                        st.Units AS units
        FROM {_qualified_table('SensorData')} sd
        LEFT JOIN {_qualified_table('SensorTypes')} st
          ON sd.SensorId = st.SensorId
        JOIN {_qualified_table('Workouts')} w
          ON sd.WorkoutID = w.WorkoutId
        WHERE w.UserId = @user_id
          AND sd.WorkoutID = @workout_id
        ORDER BY sd.Timestamp ASC
    """
    params = [
        bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
        bigquery.ScalarQueryParameter('workout_id', 'STRING', workout_id),
    ]
    rows = _query(sql, params)
    return [
        {
            'sensor_type': row['sensor_type'],
            'timestamp': _format_datetime(row['timestamp']),
            'data': row['data'],
            'units': row['units'],
        }
        for row in rows
    ]


def get_user_workouts(user_id):
    """Returns a list of workouts for the given user."""
    sql = f"""
        SELECT
            WorkoutId,
            StartTimestamp,
            EndTimestamp,
            StartLocationLat,
            StartLocationLong,
            EndLocationLat,
            EndLocationLong,
            TotalDistance,
            TotalSteps,
            CaloriesBurned,
            DATETIME_DIFF(EndTimestamp, StartTimestamp, MINUTE) AS DurationMinutes
        FROM {_qualified_table('Workouts')}
        WHERE UserId = @user_id
        ORDER BY StartTimestamp DESC
    """
    params = [bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)]
    rows = _query(sql, params)
    workouts = []
    for row in rows:
        workouts.append(
            {
                'workout_id': row['WorkoutId'],
                'start_timestamp': _format_datetime(row['StartTimestamp']),
                'end_timestamp': _format_datetime(row['EndTimestamp']),
                'start_lat_lng': (row['StartLocationLat'], row['StartLocationLong']),
                'end_lat_lng': (row['EndLocationLat'], row['EndLocationLong']),
                'distance': row['TotalDistance'],
                'steps': row['TotalSteps'],
                'calories_burned': row['CaloriesBurned'],
                # These aliases match existing UI helpers in modules.py.
                'duration': row['DurationMinutes'] or 0,
                'calories': row['CaloriesBurned'] or 0,
            }
        )
    return workouts


def get_user_profile(user_id):
    """Returns profile information for the given user."""
    profile_sql = f"""
        SELECT UserId, Name, Username, ImageUrl, DateOfBirth
        FROM {_qualified_table('Users')}
        WHERE UserId = @user_id
        LIMIT 1
    """
    friend_sql = f"""
        SELECT
            CASE
                WHEN UserId1 = @user_id THEN UserId2
                ELSE UserId1
            END AS friend_id
        FROM {_qualified_table('Friends')}
        WHERE UserId1 = @user_id OR UserId2 = @user_id
    """

    params = [bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)]
    profile_rows = list(_query(profile_sql, params))
    if not profile_rows:
        raise ValueError(f'User {user_id} not found.')

    profile = profile_rows[0]
    friend_rows = _query(friend_sql, params)
    friends = [row['friend_id'] for row in friend_rows]

    return {
        'full_name': profile['Name'],
        'username': profile['Username'],
        'date_of_birth': str(profile['DateOfBirth']),
        'profile_image': profile['ImageUrl'],
        'friends': friends,
    }


def get_user_posts(user_id):
    """Returns a list of posts authored by the given user."""
    sql = f"""
        SELECT PostId, AuthorId, Timestamp, ImageUrl, Content
        FROM {_qualified_table('Posts')}
        WHERE AuthorId = @user_id
        ORDER BY Timestamp DESC
    """
    params = [bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)]
    rows = _query(sql, params)
    return [
        {
            'user_id': row['AuthorId'],
            'post_id': row['PostId'],
            'timestamp': _format_datetime(row['Timestamp']),
            'content': row['Content'],
            'image': row['ImageUrl'],
        }
        for row in rows
    ]


def get_genai_advice(user_id):
    """Returns recent advice generated from user profile and workouts."""
    sql = f"""
        SELECT WorkoutId, StartTimestamp, TotalDistance, TotalSteps, CaloriesBurned
        FROM {_qualified_table('Workouts')}
        WHERE UserId = @user_id
        ORDER BY StartTimestamp DESC
        LIMIT 1
    """
    params = [bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)]
    rows = list(_query(sql, params))
    profile = get_user_profile(user_id)

    if not rows:
        content = 'No workouts found yet. Log your first session and I will tailor your advice.'
        return {
            'advice_id': 'advice-no-workout',
            'timestamp': _format_datetime(datetime.utcnow()),
            'content': content,
            'image': random.choice([None, random.choice(MOTIVATIONAL_IMAGES)]),
        }

    latest = rows[0]
    default_content = (
        f"Great momentum, {profile['username']}. Your latest workout covered "
        f"{latest['TotalDistance']} miles, {latest['TotalSteps']} steps, and "
        f"{latest['CaloriesBurned']} calories burned. "
        'Try adding one extra interval in your next session.'
    )

    content = default_content
    if genai and GEMINI_API_KEY:
        prompt = (
            'You are a fitness coach. Write 2-3 encouraging sentences using this data. '
            f"User: {profile['username']}. "
            f"Latest workout: distance={latest['TotalDistance']}, "
            f"steps={latest['TotalSteps']}, calories={latest['CaloriesBurned']}."
        )
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            if response and getattr(response, 'text', None):
                content = response.text.strip()
        except Exception:
            content = default_content

    return {
        'advice_id': f"advice-{latest['WorkoutId']}",
        'timestamp': _format_datetime(latest['StartTimestamp']),
        'content': content,
        'image': random.choice([None, random.choice(MOTIVATIONAL_IMAGES)]),
    }

def create_user_post(author_id, content, image_url=''):
    """Inserts a new post row into Posts and returns the inserted post data."""
    post_id = f"post-{author_id}-{int(datetime.utcnow().timestamp())}"
    created_at = datetime.utcnow()

    sql = f"""
        INSERT INTO {_qualified_table('Posts')} (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES (@post_id, @author_id, @timestamp, @image_url, @content)
    """
    params = [
        bigquery.ScalarQueryParameter('post_id', 'STRING', post_id),
        bigquery.ScalarQueryParameter('author_id', 'STRING', author_id),
        bigquery.ScalarQueryParameter('timestamp', 'TIMESTAMP', created_at),
        bigquery.ScalarQueryParameter('image_url', 'STRING', image_url),
        bigquery.ScalarQueryParameter('content', 'STRING', content),
    ]
    _query(sql, params)

    return {
        'user_id': author_id,
        'post_id': post_id,
        'timestamp': _format_datetime(created_at),
        'content': content,
        'image': image_url,
    }