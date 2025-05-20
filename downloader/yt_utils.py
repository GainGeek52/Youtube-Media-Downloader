import os
from yt_dlp import YoutubeDL

# Add this missing video download function
def download_video(url: str, out_dir: str) -> str:
    """Download video with audio stream"""
    ydl_opts = {
        'outtmpl': os.path.join(out_dir, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
        'retries': 3
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        raise RuntimeError(f"Video download failed: {str(e)}")

# Rest of your existing audio and transcript functions...

def download_audio_and_get_path(url, out_dir):
    ydl_opts = {
        'outtmpl': os.path.join(out_dir, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            mp3_file = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            # Return absolute path
            return os.path.abspath(mp3_file), info.get('title', 'audio')
            
    except Exception as e:
        raise RuntimeError(f"Audio download failed: {str(e)}")