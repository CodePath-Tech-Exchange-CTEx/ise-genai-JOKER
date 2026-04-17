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
    """Generate a random user id that does not already exist in Users."""
    existing_query = "SELECT UserId FROM `robert-hardy-hu.JOKER.Users`"
    existing_ids = {row['UserId'] for row in client.query(existing_query).result()}

    for _ in range(1000):
        candidate = f"user{random.randint(100000, 999999)}"
        if candidate not in existing_ids:
            return candidate

    raise RuntimeError("Unable to generate a unique user id after many attempts.")


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
    existing_query = "SELECT PostId FROM `robert-hardy-hu.JOKER.Posts`"
    existing_ids = {row['PostId'] for row in client.query(existing_query).result()}

    post_id = None
    for _ in range(1000):
        candidate = f"post{random.randint(100000, 999999)}"
        if candidate not in existing_ids:
            post_id = candidate
            break

    if not post_id:
        raise RuntimeError('Unable to generate a unique post id.')

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

    return {
        'user_id': author_id,
        'post_id': post_id,
        'timestamp': created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'content': cleaned_content,
        'image': cleaned_image_url,
        'likes': 0,
        'comments': [],
    }
