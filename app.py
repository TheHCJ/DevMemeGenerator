import os
import praw
import random
from flask import Flask, jsonify, send_file
import io
import requests

# Initialize the Flask app
app = Flask(__name__)

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

@app.route("/meme", methods=["GET"])
def meme():
    # Fetch top posts from r/ProgrammerHumor
    subreddit = reddit.subreddit("ProgrammerHumor")
    posts = subreddit.top(limit=10)  # Get top 10 posts

    # Randomly select one post
    post = random.choice(list(posts))

    # Check if the post has an image
    if post.url.endswith(('.jpg', '.jpeg', '.png')):
        # Download the image
        img_response = requests.get(post.url)
        img_response.raise_for_status()  # Raise an exception if the request failed
        
        # Return the image
        return send_file(io.BytesIO(img_response.content), mimetype='image/jpeg')
    
    # If no image found, return a message
    return jsonify({"error": "No image found."})

if __name__ == "__main__":
    app.run(debug=True)
