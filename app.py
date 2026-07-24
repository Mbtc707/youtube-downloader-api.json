from flask import Flask, request, jsonify
import yt_dlp

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
        # YouTube Bot Check ကို ကျော်လွှားရန် Mobile Client များ သုံးခြင်း
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios']
                }
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            title = info.get('title')

            return jsonify({
                'status': 'success',
                'title': title,
                'download_url': download_url
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


