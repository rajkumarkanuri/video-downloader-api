from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Enable CORS so your Blogger site is allowed to make requests
CORS(app)

@app.route('/api/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Missing URL parameter'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        'extract_flat': False
        'cookiefile': 'cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle single video or first entry in a playlist/carousel
            video_data = info['entries'][0] if 'entries' in info else info
            
            download_url = video_data.get('url')
            # Fallback if top-level direct URL is omitted
            if not download_url and video_data.get('formats'):
                download_url = video_data['formats'][-1].get('url')

            return jsonify({
                'status': 'success',
                'title': video_data.get('title', 'Social Media Video'),
                'thumbnail': video_data.get('thumbnail', ''),
                'download_url': download_url
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)