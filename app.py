from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# အလုပ်လုပ်နေသည့် Piped Public Instances စာရင်း
PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.mha.fi",
    "https://pipedapi.adminforge.de",
    "https://piped-api.garudalinux.org"
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

    # Instance တစ်ခုချင်းစီကို ပတ်ပြီး စမ်းခေါ်ခြင်း
    data = None
    for instance in PIPED_INSTANCES:
        try:
            piped_url = f"{instance}/streams/{video_id}"
            response = requests.get(piped_url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                break # အဆင်ပြေသွားရင် loop ထဲက ထွက်မည်
        except Exception:
            continue # အဆင်မပြေပါက နောက်တစ်လုံးသို့ ဆက်သွားမည်

    if not data:
        return jsonify({'status': 'error', 'message': 'All API instances are down. Please try again later.'}), 500

    try:
        video_streams = data.get("videoStreams", [])
        
        # 720p / 480p / 360p အဆင်ပြေဆုံး stream link ကို ယူခြင်း
        download_url = None
        for stream in video_streams:
            if stream.get("quality") in ["720p", "1080p", "480p", "360p"]:
                download_url = stream.get("url")
                break
        
        if not download_url and len(video_streams) > 0:
            download_url = video_streams[0].get("url")

        title = data.get("title", "YouTube Video")

        if download_url:
            return jsonify({
                'status': 'success',
                'title': title,
                'download_url': download_url
            })
        else:
            return jsonify({'status': 'error', 'message': 'No download streams found'}), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500






