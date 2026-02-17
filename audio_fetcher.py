import yt_dlp
import os

def download_audio(url, output_dir="./temp", use_cookies=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Downloading audio from {url}...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'quiet': False,
    }
    
    if use_cookies:
        # Tries to get cookies from Chrome.
        # Can be changed to 'firefox' or others if needed, but Chrome is a safe default.
        ydl_opts['cookiesfrombrowser'] = ('chrome',)

    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # expected filename after post-processing
        final_filename = os.path.splitext(filename)[0] + ".wav"
        
        return final_filename, info.get('title', 'Unknown Song')
