from google.cloud import bigquery
import random
from datetime import datetime
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyCUwvjVDxFk75RHFbJ9ljnIvYnhilv6xqM"
def get_bq_client():
    return bigquery.Client()

def get_user_by_username(username):
    """Returns a user record for a given username, or None if not found."""
    cleaned_username = (username or "").strip()
    if not cleaned_username:
        return None

    client = get_bq_client()
    query = """
        SELECT UserId as user_id, Name as full_name, Username as username
        FROM `robert-hardy-hu.JOKER.Users`
        WHERE LOWER(Username) = LOWER(@username)
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('username', 'STRING', cleaned_username),
        ]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return dict(rows[0]) if rows else None


def _generate_unique_user_id(client):
    """Generate a random user id that does not already exist in Users."""
    existing_query = "SELECT UserId FROM `robert-hardy-hu.JOKER.Users`"
    existing_ids = {row['UserId'] for row in client.query(existing_query).result()}

    for _ in range(1000):
        candidate = f"user{random.randint(100000, 999999)}"
        if candidate not in existing_ids:
            return candidate

    raise RuntimeError("Unable to generate a unique user id after many attempts.")


def create_user_account(name, username):
    """Creates a new user with name and username and returns the user record."""
    cleaned_name = (name or "").strip()
    cleaned_username = (username or "").strip()

    if not cleaned_name or not cleaned_username:
        raise ValueError("Name and username are required.")

    if get_user_by_username(cleaned_username):
        raise ValueError("That username is already taken.")

    client = get_bq_client()
    user_id = _generate_unique_user_id(client)

    insert_query = """
        INSERT INTO `robert-hardy-hu.JOKER.Users` (UserId, Name, Username)
        VALUES (@user_id, @name, @username)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
            bigquery.ScalarQueryParameter('name', 'STRING', cleaned_name),
            bigquery.ScalarQueryParameter('username', 'STRING', cleaned_username),
        ]
    )
    client.query(insert_query, job_config=job_config).result()

    return {
        'user_id': user_id,
        'full_name': cleaned_name,
        'username': cleaned_username,
    }
    
def get_user_sensor_data(user_id, workout_id):
    """Returns a list of timestampped information for a given workout.
    """
    client = get_bq_client()
    query = f"""
        SELECT t.Name as sensor_type, d.Timestamp as timestamp, 
               d.SensorValue as data, t.Units as units
        FROM `robert-hardy-hu.JOKER.SensorData` d
        JOIN `robert-hardy-hu.JOKER.SensorTypes` t ON d.SensorId = t.SensorId
        WHERE d.WorkoutID = '{workout_id}'
        ORDER BY d.Timestamp ASC
    """

    results = client.query(query).result()
    return [dict(row) for row in results]


def get_user_workouts(user_id):
    """Returns a list of user's workouts.
    """
    client = get_bq_client()
    query = f"""
        SELECT WorkoutId as workout_id, StartTimestamp as start_timestamp, 
               EndTimestamp as end_timestamp, StartLocationLat as start_lat_lng_lat, 
               StartLocationLong as start_lat_lng_lng, TotalDistance as distance, 
               TotalSteps as steps, CaloriesBurned as calories_burned
        FROM `robert-hardy-hu.JOKER.Workouts`
        WHERE UserId = '{user_id}'
        ORDER BY StartTimestamp DESC
    """

    results = client.query(query).result()
    
    workouts = []
    for row in results:
        w = dict(row)
        if w['start_timestamp'] and w['end_timestamp']:
            delta = w['end_timestamp'] - w['start_timestamp']
            w['duration'] = int(delta.total_seconds() / 60)
        workouts.append(w)
    return workouts


def get_user_profile(user_id):
    """Returns information about the given user.
    """
    client = get_bq_client()
    query = f"""
        SELECT 
            Name as full_name, 
            Username as username, 
            DateOfBirth as date_of_birth, 
            ImageUrl as profile_image 
        FROM `robert-hardy-hu.JOKER.Users` 
        WHERE UserId = '{user_id}'
    """
    results = list(client.query(query).result())
    
    if not results:
        return None
        
    profile = dict(results[0])
    
    friends_query = f"SELECT UserId2 FROM `robert-hardy-hu.JOKER.Friends` WHERE UserId1 = '{user_id}'"
    friends_results = client.query(friends_query).result()
    profile['friends'] = [row['UserId2'] for row in friends_results]
    
    return profile


def get_user_posts(user_id):
    """Returns a list of a user's posts.
    """
    client = get_bq_client()
    query = f"""
        SELECT PostId as post_id, AuthorId as user_id, Timestamp as timestamp, 
               ImageUrl as image, Content as content
        FROM `robert-hardy-hu.JOKER.Posts`
        WHERE AuthorId = '{user_id}'
        ORDER BY Timestamp DESC
    """

    results = client.query(query).result()
    return [dict(row) for row in results]


def get_genai_advice(user_id):
    """
    Fetches personalized fitness advice from Gemini based on user stats.
    """
    # 1. Gather the "Information" to base the advice on
    workouts = get_user_workouts(user_id)
    total_cals = sum(w.get('calories_burned', 0) for w in workouts)
    total_steps = sum(w.get('steps', 0) for w in workouts)
   
    # 2. Setup the Gemini Model
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
   
    # 3. Craft a prompt that tells the AI about the user
    prompt = f"""
        You are a supportive personal trainer.
        A user has burned {total_cals} calories and taken {total_steps} steps in their recent workouts.
        Give them one specific, encouraging piece of fitness advice in 2 sentences or less.
    """
   
    try:
        response = model.generate_content(prompt)
        advice_content = response.text.strip()
    except Exception as e:
        advice_content = "Keep pushing! Every step counts toward your goals."


    # 4. Handle optional images (e.g., 60% chance of an image)
    MOTIVATIONAL_IMAGES = [
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
        "https://images.unsplash.com/photo-1599058917212-d750089bc07e",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b"
    ]
   
    # Logic: Only pick an image if random check passes
    image_url = random.choice(MOTIVATIONAL_IMAGES) if random.random() > 0.4 else None


    return {
        'advice_id': f'genai_{random.randint(100, 999)}',
        'timestamp': datetime.now(),
        'content': advice_content,
        'image': image_url,
    }

def create_user_post(author_id, content, image_url=''):
    """Inserts a new post row into Posts and returns the inserted post data."""
    post_id = f"post-{author_id}-{int(datetime.utcnow().timestamp())}"
    created_at = datetime.utcnow()

    client = get_bq_client()
    query = """
        INSERT INTO `robert-hardy-hu.JOKER.Posts` (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES (@post_id, @author_id, @timestamp, @image_url, @content)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('post_id', 'STRING', post_id),
            bigquery.ScalarQueryParameter('author_id', 'STRING', author_id),
            bigquery.ScalarQueryParameter('timestamp', 'DATETIME', created_at),
            bigquery.ScalarQueryParameter('image_url', 'STRING', image_url),
            bigquery.ScalarQueryParameter('content', 'STRING', content),
        ]
    )
    client.query(query, job_config=job_config).result()

    return {
        'user_id': author_id,
        'post_id': post_id,
        'timestamp': created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'content': content,
        'image': image_url,
    }
