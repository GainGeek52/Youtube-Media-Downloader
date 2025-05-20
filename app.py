import os
from flask import Flask, render_template, request, send_file, flash
from downloader.yt_utils import download_video, download_audio_and_get_path, download_transcript
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32).hex())

# Configure paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, 'downloads')

# Ensure downloads directory exists
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        mode = request.form.get('mode')
        
        if not url or not mode:
            flash('❌ Please provide both URL and mode', 'error')
            return render_template('index.html')
        
        try:
            if mode == 'video':
                file_path = download_video(url, DOWNLOADS_DIR)
                filename = os.path.basename(file_path)
                return send_file(file_path, as_attachment=True, download_name=filename)
            
            elif mode == 'audio':
                file_path, title = download_audio_and_get_path(url, DOWNLOADS_DIR)
                filename = f"{title}.mp3"
                return send_file(file_path, as_attachment=True, download_name=filename)
            
            elif mode == 'transcript':
                file_path = download_transcript(url, DOWNLOADS_DIR)
                filename = os.path.basename(file_path)
                return send_file(file_path, as_attachment=True, download_name=filename)
            
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            flash(f'❌ Download failed: {str(e)}', 'error')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)