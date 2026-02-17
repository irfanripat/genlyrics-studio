import cv2
import numpy as np
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

def wrap_text_pil(text, font, max_width):
    """
    Wrap text using PIL font metrics.
    """
    lines = []
    if not text:
        return lines
        
    words = text.split(' ')
    current_line = []
    
    for word in words:
        current_line.append(word)
        # Check width
        test_line = ' '.join(current_line)
        bbox = font.getbbox(test_line) # left, top, right, bottom
        w = bbox[2] - bbox[0]
        
        if w > max_width and len(current_line) > 1:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(' '.join(current_line))
        
    return lines

def create_lyrics_video(audio_path, segments, output_path="output.mp4", 
                        bg_image_path=None, font_path=None, 
                        color_active=(255, 230, 0, 255), 
                        color_inactive=(200, 200, 200, 180)):
    print(f"Rendering video to {output_path}...")
    
    # Video settings
    fps = 30
    width, height = 1920, 1080
    max_text_width = int(width * 0.8)
    
    # Load Font
    font_size = 60
    if not font_path:
        font_path = "/System/Library/Fonts/Avenir Next.ttc"
        
    try:
        font = ImageFont.truetype(font_path, font_size, index=0)
    except Exception as e:
        print(f"Could not load font {font_path}: {e}. Falling back to default.")
        font = ImageFont.load_default()
    
    # Colors
    color_shadow = (0, 0, 0, 128) # Black shadow
    
    # Load background
    if bg_image_path and os.path.exists(bg_image_path):
        pil_bg = Image.open(bg_image_path).convert('RGBA')
        pil_bg = pil_bg.resize((width, height), Image.Resampling.LANCZOS)
        # Darken overlay
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
        pil_bg = Image.alpha_composite(pil_bg, overlay)
    else:
        # Default gradient or solid color
        pil_bg = Image.new('RGBA', (width, height), (20, 20, 30, 255))
        
    # Duration
    last_end = segments[-1]['end'] if segments else 10
    total_frames = int((last_end + 3) * fps)
    
    # Video Writer
    temp_video = "temp_video.mp4" # mp4 slightly better container for intermediate
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    print(f"Total frames: {total_frames}")
    
    for i in range(total_frames):
        current_time = i / fps
        
        # 1. Create canvas from background
        # We process in RGBA for transparency tricks, convert to BGR for OpenCV
        canvas = pil_bg.copy()
        draw = ImageDraw.Draw(canvas)
        
        # 2. Find Segment
        current_segment = None
        for seg in segments:
            if seg['start'] <= current_time <= seg['end']:
                current_segment = seg
                break
                
        if current_segment:
            full_text = current_segment['text'].strip()
            words_info = current_segment.get('words', [])
            
            lines = wrap_text_pil(full_text, font, max_text_width)
            
            # Calculate metrics for vertical centering
            # Get line height
            bbox = font.getbbox("Tg")
            line_height = (bbox[3] - bbox[1]) * 1.5 # 1.5 spacing
            total_text_height = len(lines) * line_height
            
            start_y = (height - total_text_height) // 2
            
            current_word_idx = 0
            
            for line_idx, line in enumerate(lines):
                line_words = line.split(' ')
                
                # Calculate line width to center horizontally
                line_bbox = font.getbbox(line)
                line_w = line_bbox[2] - line_bbox[0]
                start_x = (width - line_w) // 2
                
                cursor_x = start_x
                line_y = start_y + (line_idx * line_height)
                
                for word_str in line_words:
                    if not word_str: continue
                    
                    # Timing Check
                    t_start, t_end = 0, 0
                    if current_word_idx < len(words_info):
                        w_obj = words_info[current_word_idx]
                        t_start = w_obj['start']
                        t_end = w_obj['end']
                        current_word_idx += 1
                        
                    is_active = (t_start <= current_time <= t_end)
                    is_sung = (current_time > t_end)
                    
                    # Draw Color
                    if is_active:
                        fill_color = color_active
                        # Glow / Stroke for active word
                        # Simple shadow first
                        draw.text((cursor_x + 2, line_y + 2), word_str, font=font, fill=color_shadow)
                    elif is_sung:
                        fill_color = (255, 255, 255, 255) # Bright White
                    else:
                        fill_color = color_inactive
                        
                    draw.text((cursor_x, line_y), word_str, font=font, fill=fill_color)
                    
                    # Advance cursor
                    w_bbox = font.getbbox(word_str + " ")
                    w_len = w_bbox[2] - w_bbox[0]
                    cursor_x += w_len

        # Convert PIL -> OpenCV (RGB -> BGR)
        frame_np = np.array(canvas.convert('RGB'))
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        
        out.write(frame_bgr)
        
        if i % 50 == 0:
            print(f"Rendered {i}/{total_frames}", end='\r')
            
    out.release()
    print("\nEncoding final video...")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', temp_video,
        '-i', audio_path,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(temp_video):
        os.remove(temp_video)
    
    print(f"Done! {output_path}")
