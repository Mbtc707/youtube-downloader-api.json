from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube Downloader API is Running!"

@app.route('/extract', methods=['GET'])
def extract():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'status': 'error', 'message': 'URL parameter is missing'}), 400

    try:
        # Cobalt Public API သို့ လှမ်းတောင်းခြင်း
        cobalt_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": video_url,
            "vQuality": "720"
        }

        response = requests.post(cobalt_url, json=payload, headers=headers)
        data = response.json()

        if "url" in data:
            return jsonify({
                'status': 'success',
                'title': 'YouTube Video',
                'download_url': data['url']
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to extract video'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



