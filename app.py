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

    # We remove the 'format' line entirely so yt-dlp NEVER crashes on format selection
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'cookiefile': 'cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Tell yt-dlp to just fetch the data, no downloading
            info = ydl.extract_info(url, download=False)
            
            # Handle if the URL is a playlist/profile
            video_data = info['entries'][0] if 'entries' in info else info
            
            download_url = None
            
            # Look at all available formats the video has
            formats = video_data.get('formats', [])
            
            # Filter to ONLY formats that contain BOTH video and audio
            merged_formats = [
                f for f in formats 
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
            ]
            
            if merged_formats:
                # Sort them by quality (height) and grab the best one (the last item)
                merged_formats = sorted(merged_formats, key=lambda x: x.get('height', 0) or 0)
                download_url = merged_formats[-1].get('url')
            else:
                # If no merged formats exist, fallback to the default URL
                download_url = video_data.get('url')
                if not download_url and formats:
                    download_url = formats[-1].get('url')

            if not download_url:
                raise Exception("Could not find a playable download link for this video.")

            return jsonify({
                'status': 'success',
                'title': video_data.get('title', 'Social Media Video'),
                'thumbnail': video_data.get('thumbnail', ''),
                'download_url': download_url
            })
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500