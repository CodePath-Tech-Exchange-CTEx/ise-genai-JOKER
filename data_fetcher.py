from google.cloud import bigquery
import random
from datetime import datetime
import uuid
import google.generativeai as genai
import streamlit as st

GEMINI_API_KEY = "AIzaSyCUwvjVDxFk75RHFbJ9ljnIvYnhilv6xqM"
def get_bq_client():
    return bigquery.Client()

def _clear_cached_reads():
    """Clears cached read results after writes."""
    st.cache_data.clear()


def _id_exists(client, table, column, value):
    """Returns True when an id already exists in a table."""
    query = f"""
        SELECT 1
        FROM `{table}`
        WHERE {column} = @value
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('value', 'STRING', value),
        ]
    )
    return bool(list(client.query(query, job_config=job_config).result()))


def _generate_unique_id(client, table, column, prefix):
    """Generates a unique id using UUID and verifies it does not exist."""
    for _ in range(20):
        candidate = f"{prefix}{uuid.uuid4().hex[:10]}"
        if not _id_exists(client, table, column, candidate):
            return candidate
    raise RuntimeError(f"Unable to generate a unique {prefix} id.")


@st.cache_data(ttl=60)

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

def authenticate_user(username, password):
    """Returns a user record only when username/password are valid."""
    cleaned_username = (username or "").strip()
    cleaned_password = (password or "").strip()
    if not cleaned_username or not cleaned_password:
        return None

    client = get_bq_client()
    query = """
        SELECT UserId as user_id, Name as full_name, Username as username
        FROM `robert-hardy-hu.JOKER.Users`
        WHERE LOWER(Username) = LOWER(@username)
          AND Password = @password
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('username', 'STRING', cleaned_username),
            bigquery.ScalarQueryParameter('password', 'STRING', cleaned_password),
        ]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return dict(rows[0]) if rows else None

def _generate_unique_user_id(client):
    """Generate a unique user id without scanning the full Users table."""
    return _generate_unique_id(client, 'robert-hardy-hu.JOKER.Users', 'UserId', 'user')


def create_user_account(name, username, password):
    """Creates a new user with name and username and returns the user record."""
    cleaned_name = (name or "").strip()
    cleaned_username = (username or "").strip()
    cleaned_password = (password or "").strip()

    if not cleaned_name or not cleaned_username or not cleaned_password:
        raise ValueError("Name, username, and password are required.")

    if get_user_by_username(cleaned_username):
        raise ValueError("That username is already taken.")

    client = get_bq_client()
    user_id = _generate_unique_user_id(client)

    insert_query = """
        INSERT INTO `robert-hardy-hu.JOKER.Users` (UserId, Name, Username, Password)
        VALUES (@user_id, @name, @username, @password)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
            bigquery.ScalarQueryParameter('name', 'STRING', cleaned_name),
            bigquery.ScalarQueryParameter('username', 'STRING', cleaned_username),
            bigquery.ScalarQueryParameter('password', 'STRING', cleaned_password),
        ]
    )
    client.query(insert_query, job_config=job_config).result()
    _clear_cached_reads()

    return {
        'user_id': user_id,
        'full_name': cleaned_name,
        'username': cleaned_username,
    }
@st.cache_data(ttl=60)
    
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

@st.cache_data(ttl=60)
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

@st.cache_data(ttl=60)
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

def update_user_profile_details(user_id, image_url, date_of_birth):
    """Updates a user's profile image URL and date of birth."""
    cleaned_image_url = (image_url or '').strip()
    if not date_of_birth:
        raise ValueError('Date of birth is required.')

    client = get_bq_client()
    query = """
        UPDATE `robert-hardy-hu.JOKER.Users`
        SET ImageUrl = @image_url,
            DateOfBirth = @date_of_birth
        WHERE UserId = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('image_url', 'STRING', cleaned_image_url),
            bigquery.ScalarQueryParameter('date_of_birth', 'DATE', date_of_birth),
            bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
        ]
    )
    client.query(query, job_config=job_config).result()
    _clear_cached_reads()

def update_user_password(user_id, new_password):
    """Updates a user's password."""
    cleaned_password = (new_password or '').strip()
    if not cleaned_password:
        raise ValueError('Password is required.')

    client = get_bq_client()
    query = """
        UPDATE `robert-hardy-hu.JOKER.Users`
        SET Password = @password
        WHERE UserId = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('password', 'STRING', cleaned_password),
            bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
        ]
    )
    client.query(query, job_config=job_config).result()
    _clear_cached_reads()

@st.cache_data(ttl=60)  
def get_people_you_may_know(user_id, limit=5):
    """Returns users that are not the current user and not already friends."""
    client = get_bq_client()
    safe_limit = max(1, int(limit))
    query = f"""
        SELECT
            u.UserId as user_id,
            u.Name as full_name,
            u.Username as username,
            u.ImageUrl as profile_image
        FROM `robert-hardy-hu.JOKER.Users` u
        WHERE u.UserId != @user_id
          AND u.UserId NOT IN (
              SELECT UserId2
              FROM `robert-hardy-hu.JOKER.Friends`
              WHERE UserId1 = @user_id
          )
        ORDER BY u.Username
        LIMIT {safe_limit}
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
        ]
    )
    return [dict(row) for row in client.query(query, job_config=job_config).result()]


def add_friend(user_id, friend_user_id):
    """Stores a friend relationship UserId1 -> UserId2 if not already present."""
    cleaned_user_id = (user_id or '').strip()
    cleaned_friend_user_id = (friend_user_id or '').strip()

    if not cleaned_user_id or not cleaned_friend_user_id:
        raise ValueError('Both user ids are required.')
    if cleaned_user_id == cleaned_friend_user_id:
        raise ValueError('You cannot add yourself as a friend.')

    client = get_bq_client()
    exists_query = """
        SELECT 1
        FROM `robert-hardy-hu.JOKER.Friends`
        WHERE UserId1 = @user_id AND UserId2 = @friend_user_id
        LIMIT 1
    """
    exists_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('user_id', 'STRING', cleaned_user_id),
            bigquery.ScalarQueryParameter('friend_user_id', 'STRING', cleaned_friend_user_id),
        ]
    )
    already_exists = list(client.query(exists_query, job_config=exists_job_config).result())
    if already_exists:
        return

    insert_query = """
        INSERT INTO `robert-hardy-hu.JOKER.Friends` (UserId1, UserId2)
        VALUES (@user_id, @friend_user_id)
    """
    client.query(insert_query, job_config=exists_job_config).result()
    _clear_cached_reads()

@st.cache_data(ttl=60)
def get_friend_feed(user_id, limit=10):
    """Returns recent posts from friends using one query."""
    safe_limit = max(1, int(limit))
    client = get_bq_client()
    query = f"""
        SELECT
            p.PostId as post_id,
            p.Timestamp as timestamp,
            p.Content as content,
            p.ImageUrl as post_image,
            COALESCE(p.Likes, 0) as likes,
            IFNULL(p.Comments, []) as comments,
            u.Username as username,
            u.ImageUrl as user_image
        FROM `robert-hardy-hu.JOKER.Friends` f
        JOIN `robert-hardy-hu.JOKER.Posts` p ON p.AuthorId = f.UserId2
        JOIN `robert-hardy-hu.JOKER.Users` u ON u.UserId = f.UserId2
        WHERE f.UserId1 = @user_id
        ORDER BY p.Timestamp DESC
        LIMIT {safe_limit}
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('user_id', 'STRING', user_id),
        ]
    )
    return [dict(row) for row in client.query(query, job_config=job_config).result()]

@st.cache_data(ttl=60)
def get_user_posts(user_id):
    """Returns a list of a user's posts.
    """
    client = get_bq_client()
    query = f"""
        SELECT PostId as post_id, AuthorId as user_id, Timestamp as timestamp,
               ImageUrl as image, Content as content,
               COALESCE(Likes, 0) as likes, IFNULL(Comments, []) as comments
        FROM `robert-hardy-hu.JOKER.Posts`
        WHERE AuthorId = '{user_id}'
        ORDER BY Timestamp DESC
    """

    results = client.query(query).result()
    posts = []
    for row in results:
        post = dict(row)
        if post.get('comments') is None:
            post['comments'] = []
        posts.append(post)
    return posts


def increment_post_likes(post_id):
    """Increments the like counter for a post by 1."""
    client = get_bq_client()
    query = """
        UPDATE `robert-hardy-hu.JOKER.Posts`
        SET Likes = COALESCE(Likes, 0) + 1
        WHERE PostId = @post_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('post_id', 'STRING', post_id),
        ]
    )
    client.query(query, job_config=job_config).result()
    _clear_cached_reads()

def append_post_comment(post_id, comment):
    """Appends a comment string to a post's Comments array."""
    cleaned_comment = (comment or '').strip()
    if not cleaned_comment:
        return

    client = get_bq_client()
    query = """
        UPDATE `robert-hardy-hu.JOKER.Posts`
        SET Comments = ARRAY_CONCAT(IFNULL(Comments, []), [@comment])
        WHERE PostId = @post_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('post_id', 'STRING', post_id),
            bigquery.ScalarQueryParameter('comment', 'STRING', cleaned_comment),
        ]
    )
    client.query(query, job_config=job_config).result()
    _clear_cached_reads()

@st.cache_data(ttl=120)
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
    cleaned_content = (content or '').strip()
    cleaned_image_url = (image_url or '').strip()
    if not cleaned_content:
        raise ValueError('Post content is required.')

    client = get_bq_client()
    post_id = _generate_unique_id(client, 'robert-hardy-hu.JOKER.Posts', 'PostId', 'post')
    created_at = datetime.utcnow().replace(microsecond=0)
    query = """
        INSERT INTO `robert-hardy-hu.JOKER.Posts` (PostId, AuthorId, Timestamp, ImageUrl, Content, Likes, Comments)
        VALUES (@post_id, @author_id, @timestamp, @image_url, @content, @likes, @comments)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('post_id', 'STRING', post_id),
            bigquery.ScalarQueryParameter('author_id', 'STRING', author_id),
            bigquery.ScalarQueryParameter('timestamp', 'DATETIME', created_at),
            bigquery.ScalarQueryParameter('image_url', 'STRING', cleaned_image_url),
            bigquery.ScalarQueryParameter('content', 'STRING', cleaned_content),
            bigquery.ScalarQueryParameter('likes', 'INT64', 0),
            bigquery.ArrayQueryParameter('comments', 'STRING', []),
        ]
    )
    client.query(query, job_config=job_config).result()
    _clear_cached_reads()

    return {
        'user_id': author_id,
        'post_id': post_id,
        'timestamp': created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'content': cleaned_content,
        'image': cleaned_image_url,
        'likes': 0,
        'comments': [],
    }
