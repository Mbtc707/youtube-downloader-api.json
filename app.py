from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# YouTube URL မှ Video ID သီးသန့် ထုတ်ယူသည့် Function
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

    try:
        # Piped API Endpoint သို့ လှမ်းတောင်းခြင်း
        piped_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.get(piped_url, headers=headers, timeout=10)
        
        # အကယ်၍ ကနဦး Instance အဆင်မပြေပါက Backup Instance သို့ ပြောင်းခေါ်ခြင်း
        if response.status_code != 200:
            piped_url = f"https://api.piped.yt/streams/{video_id}"
            response = requests.get(piped_url, headers=headers, timeout=10)

        data = response.json()

        # Video streams ထဲမှ Direct Download Link ရှာခြင်း
        video_streams = data.get("videoStreams", [])
        
        # 720p/1080p သို့မဟုတ် ရနိုင်သော အကောင်းဆုံး Stream Link ကို ယူခြင်း
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





