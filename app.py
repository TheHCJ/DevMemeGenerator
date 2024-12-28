from dotenv import load_dotenv
import os
import requests
import random
from flask import Flask, send_file, jsonify
from io import BytesIO
from PIL import Image

# Load environment variables
load_dotenv()

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
    headers = {"User-Agent": USER_AGENT}
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=auth,
        data=data,
        headers=headers,
    )
    response.raise_for_status()
    return response.json()["access_token"]

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
        if post["data"]["url"].endswith(("jpg", "png", "gif"))
    ]
    if not image_posts:
        raise Exception("No image posts found.")
    meme = random.choice(image_posts)
    return {"title": meme["title"], "url": meme["url"]}

def convert_to_webp(image_url):
    """Convert the image to WebP format."""
    response = requests.get(image_url)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))

    # Convert to WebP
    webp_image = BytesIO()
    img.save(webp_image, format="WEBP")
    webp_image.seek(0)
    return webp_image

@app.route("/random-meme", methods=["GET"])
def random_meme():
    """API endpoint to get a random developer meme."""
    try:
        access_token = get_reddit_access_token()
        meme = fetch_random_meme(access_token)
        webp_image = convert_to_webp(meme["url"])
        return send_file(
            webp_image,
            mimetype="image/webp",
            as_attachment=False,
            download_name="meme.webp"
        )
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")  # Log the error for debugging
        return jsonify({"error": "There was an issue with the Reddit API request."}), 500
    except Exception as e:
        print(f"General Error: {str(e)}")  # Log the error for debugging
        return jsonify({"error": "An unexpected error occurred."}), 500


# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
