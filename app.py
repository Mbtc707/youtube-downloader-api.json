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
        # Cobalt API Endpoint
        cobalt_url = "https://api.cobalt.tools/"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        payload = {
            "url": video_url
        }

        response = requests.post(cobalt_url, json=payload, headers=headers)
        data = response.json()

        # Cobalt response ထဲက download url ကို ရှာခြင်း
        download_url = data.get("url")
        
        # Audio / Video Picker response ဖြစ်နေပါက ပထမဆုံး link ကို ယူခြင်း
        if not download_url and "picker" in data and len(data["picker"]) > 0:
            download_url = data["picker"][0].get("url")

        if download_url:
            return jsonify({
                'status': 'success',
                'title': 'YouTube Video',
                'download_url': download_url
            })
        else:
            # Cobalt ဘက်က ပြန်ပေးသည့် error စာသားကို ဖော်ပြပေးရန်
            error_msg = data.get("text") or "Failed to extract video link"
            return jsonify({'status': 'error', 'message': error_msg}), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500




