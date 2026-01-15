import os
import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class TubePilotFinalEngine:
    def __init__(self):
        self.api_url = "https://tubepilot.ai/wp-admin/admin-ajax.php"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.59 Mobile Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://tubepilot.ai",
            "Referer": "https://tubepilot.ai/tools/youtube-data-viewer/"
        }

    def clean_html(self, text):
        if not text: return "N/A"
        # HTML tags aur extra spaces remove karne ke liye
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        return text.strip().replace('&nbsp;', ' ')

    def parse_advanced(self, html):
        # Saara data nikalne ke liye regex patterns
        data = {
            "video_metadata": {
                "title": self.extract(r"Video Title:</b>\s*(.*?)<br>", html),
                "uploaded_at": self.extract(r"Video Uploaded Date:</b>\s*(.*?)<br>", html),
                "category": self.extract(r"Video Category:</b>\s*(.*?)<br>", html),
                "duration": self.extract(r"Duration:</b>\s*(.*?)<br>", html),
                "views": self.extract(r"Views Count:</b>\s*(.*?)<br>", html),
                "likes": self.extract(r"Likes Count:</b>\s*(.*?)<br>", html),
                "comments": self.extract(r"Comments Count:</b>\s*(.*?)<br>", html),
                "tags": self.extract(r"Video Tags:</b>\s*(.*?)<br>", html),
                "description": self.extract(r"Video Description:</b>\s*<span class='ytdesc-txt'>(.*?)</span></span>", html)
            },
            "status": {
                "privacy": self.extract(r"Privacy Status:</b>\s*(.*?)<br>", html),
                "embed_allowed": self.extract(r"Is Embed Allowed:</b>\s*(.*?)<br>", html),
                "copyright_free": "Yes" if "✓ Yes" in html else "No",
                "age_restricted": "Yes" if "✓ Yes" in html.lower() and "age restricted" in html.lower() else "No"
            },
            "channel_details": {
                "name": self.extract(r"Channel Name:</b>\s*(.*?)<br>", html),
                "id": self.extract(r"Channel ID:</b>\s*(.*?)<br>", html),
                "subscribers": self.extract(r"Subscribers Count:</b>\s*(.*?)<br>", html),
                "total_videos": self.extract(r"Videos Count:</b>\s*(.*?)<br>", html),
                "total_views": self.extract(r"Total Views:</b>\s*(.*?)<br>", html),
                "joined_at": self.extract(r"Creation Date:</b>\s*(.*?)<br>", html),
                "country": self.extract(r"Country:</b>\s*(.*?)<br>", html),
                "logo": self.extract_attr(r"Logo/Profile Picture:.*?<a href=\"(.*?)\"", html)
            },
            "thumbnails": {
                "max_res": self.extract_attr(r"High Quality.*?href='(.*?)'", html),
                "standard": self.extract_attr(r"Standard Quality.*?href='(.*?)'", html)
            }
        }
        return data

    def extract(self, pattern, html):
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        return self.clean_html(match.group(1)) if match else "N/A"

    def extract_attr(self, pattern, html):
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else "N/A"

engine = TubePilotFinalEngine()

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "api": "Goddess YT Advanced Data",
        "usage": "/api/fetch?url=YOUR_YOUTUBE_URL"
    })

@app.route('/api/fetch', methods=['GET'])
def fetch_data():
    yt_url = request.args.get('url')
    if not yt_url:
        return jsonify({"success": False, "error": "URL parameter missing"}), 400
    
    try:
        payload = {"action": "yt_data_viewer", "yt_url": yt_url}
        r = requests.post(engine.api_url, headers=engine.headers, data=payload, timeout=15)
        
        if r.status_code == 200:
            result = engine.parse_advanced(r.text)
            return jsonify({"success": True, "data": result})
        return jsonify({"success": False, "error": f"Upstream error {r.status_code}"}), 500
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Render dynamic port binding
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
