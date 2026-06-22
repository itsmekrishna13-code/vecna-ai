import os
import asyncio
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from livekit import api
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('frontend', path)

@app.route('/token')
def get_token():
    try:
        api_key = os.getenv('LIVEKIT_API_KEY')
        api_secret = os.getenv('LIVEKIT_API_SECRET')
        
        if not api_key or not api_secret:
            return jsonify({'error': 'LiveKit credentials not found'}), 500

        token = api.AccessToken(api_key, api_secret)
        token.with_identity("user-frontend")
        token.with_name("Human")
        token.with_grants(api.VideoGrants(
            room_join=True,
            room="vecna-room",
        ))
        
        return jsonify({'token': token.to_jwt(), 'url': os.getenv('LIVEKIT_URL', 'ws://localhost:7880')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Web Server at http://localhost:8000")
    app.run(port=8000, debug=True)
