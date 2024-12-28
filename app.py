import os
import random
import requests
from flask import Flask, send_file, jsonify
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Reddit API credentials from environment variables
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")
SUBREDDIT = "ProgrammerHumor"

HEADERS = {"User-Agent": USER_AGENT}

def get_reddit_access_token():
    """Fetch an access token from Reddit."""
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {"grant_type": "client_credentials"}
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token", 
        auth=auth, data=data, headers=HEADERS
    )
    response.raise_for_status()
    return response.json().get("access_token")

def fetch_random_meme(access_token):
    """Fetch a random meme from the subreddit."""
    headers = {**HEADERS, "Authorization": f"bearer {access_token}"}
    response = requests.get(
        f"https://oauth.reddit.com/r/{SUBREDDIT}/hot?limit=50",
        headers=headers,
    )
    response.raise_for_status()
    posts = response.json()["data"]["children"]
    image_posts = [
        post["data"]
        for post in posts
        if post["data"]["url"].endswith(("jpg", "jpeg", "png", "gif"))
    ]
    if not image_posts:
        raise Exception("No valid image posts found.")
    
    meme = random.choice(image_posts)
    return meme["data"]["url"]

@app.route("/random-meme", methods=["GET"])
def random_meme():
    """API endpoint to return a random developer meme as an image."""
    try:
        access_token = get_reddit_access_token()
        meme_url = fetch_random_meme(access_token)

        # Fetch the image directly from Reddit and return it to the client
        response = requests.get(meme_url)
        response.raise_for_status()
        
        # Send the image directly to the user
        return send_file(BytesIO(response.content), mimetype=response.headers["Content-Type"])

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to fetch meme image."}), 500

# Vercel expects the app to be callable as a WSGI application.
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
