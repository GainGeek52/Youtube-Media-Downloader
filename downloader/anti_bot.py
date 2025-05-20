import random
import time
from yt_dlp import YoutubeDL

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36'
]

def configure_ytdl(out_dir):
    return {
        'outtmpl': os.path.join(out_dir, '%(title)s.%(ext)s'),
        'ignoreerrors': True,
        'retries': 10,
        'throttledratelimit': 1024000,
        'sleep_interval': random.randint(2, 5),
        'http_headers': {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        },
        'proxy': os.environ.get('PROXY_SERVER'),
    }

def should_retry(error, attempt):
    if attempt >= 2:
        return False
    time.sleep(2 ** (attempt + 1))
    return True

def rotate_ip():
    # Implement your IP rotation logic here
    pass