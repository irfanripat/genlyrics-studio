import argparse
import os
from audio_fetcher import download_audio
from lyrics_engine import transcribe_with_lyrics
from renderer import create_lyrics_video

def main():
    parser = argparse.ArgumentParser(description="YouTube Lyrics Video Generator")
    parser.add_argument("url", type=str, help="YouTube URL")
    parser.add_argument("--output", type=str, default="lyrics_video.mp4", help="Output filename")
    
    args = parser.parse_args()
    
    # 1. Download
    print(f"--- 1. Downloading... ---")
    audio_path, title = download_audio(args.url)
    print(f"Title: {title}")
    
    # 2. Transcribe
    print(f"--- 2. Transcribing... ---")
    
    # Isolate vocals first!
    from lyrics_engine import isolate_vocals
    vocals_path = isolate_vocals(audio_path)
    
    # Transcribe the vocals, but keep original audio for the video
    segments = transcribe_with_lyrics(vocals_path, model_size="medium")
    
    # 3. Render
    print(f"--- 3. Animating... ---")
    create_lyrics_video(audio_path, segments, output_path=args.output)

if __name__ == "__main__":
    main()
