from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# အလုပ်လုပ်နေသည့် Invidious နှင့် Piped Server များ စာရင်း
SERVERS = [
    {"type": "invidious", "url": "https://invidious.nerdvpn.de"},
    {"type": "invidious", "url": "https://inv.tux.pizza"},
    {"type": "invidious", "url": "https://invidious.drgns.space"},
    {"type": "piped", "url": "https://pipedapi.kavin.rocks"},
    {"type": "piped", "url": "https://api.piped.mha.fi"},
    {"type": "piped", "url": "https://pipedapi.adminforge.de"}
]

def extract_video_id(url):
    pattern = r"(?:v=|\/([0-9A-Za-z_-]{11}).*|near\/|v\/|embed\/|shorts\/|youtu.be\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1) or match.group(2)
    return None

@app.route('/')
def home():
    return "YouTube Downloader API is Running!"

@app.route('/extract', methods=['GET'])
def extract():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'status': 'error', 'message': 'URL parameter is missing'}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({'status': 'error', 'message': 'Invalid YouTube URL'}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Server စာရင်းကို အစဉ်လိုက် ပတ်ပြီး စမ်းခေါ်ခြင်း
    for server in SERVERS:
        try:
            if server["type"] == "invidious":
                api_url = f"{server['url']}/api/v1/videos/{video_id}"
                res = requests.get(api_url, headers=headers, timeout=4)
                if res.status_code == 200:
                    data = res.json()
                    streams = data.get("formatStreams", [])
                    if streams:
                        # Direct MP4 Download Link ရယူခြင်း
                        download_url = streams[-1].get("url") # အကောင်းဆုံး Quality ကိုယူမည်
                        title = data.get("title", "YouTube Video")
                        return jsonify({
                            'status': 'success',
                            'title': title,
                            'download_url': download_url
                        })

            elif server["type"] == "piped":
                api_url = f"{server['url']}/streams/{video_id}"
                res = requests.get(api_url, headers=headers, timeout=4)
                if res.status_code == 200:
                    data = res.json()
                    streams = data.get("videoStreams", [])
                    if streams:
                        download_url = streams[0].get("url")
                        title = data.get("title", "YouTube Video")
                        return jsonify({
                            'status': 'success',
                            'title': title,
                            'download_url': download_url
                        })
        except Exception:
            continue

    return jsonify({'status': 'error', 'message': 'All API instances are currently busy or down. Please try again.'}), 500







