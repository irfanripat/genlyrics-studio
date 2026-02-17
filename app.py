import streamlit as st
import os
import shutil
from audio_fetcher import download_audio
from lyrics_engine import transcribe_with_lyrics, isolate_vocals
from renderer import create_lyrics_video
from font_manager import GOOGLE_FONTS, get_font_path
from PIL import Image, ImageDraw, ImageFont, ImageStat
import json

# Setup
st.set_page_config(page_title="GenLyrics Studio", page_icon="�", layout="wide")

# Custom CSS for "CapCut" vibe
st.markdown("""
<style>
    .stApp {
        background-color: #121212;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #2D2D2D;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if 'segments' not in st.session_state:
    st.session_state.segments = []
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'title' not in st.session_state:
    st.session_state.title = ""
if 'color_active' not in st.session_state:
    st.session_state.color_active = "#FFE600"
if 'color_inactive' not in st.session_state:
    st.session_state.color_inactive = "#C8C8C8"


# --- LAYOUT ---
# Sidebar is now the Tool Panel (Left)
with st.sidebar:
    st.title("� GenLyrics")
    st.markdown("Create viral lyrics videos in seconds.")
    
    # --- 1. MEDIA ---
    with st.expander("📂 1. Media Source", expanded=True):
        input_method = st.radio("Source", ["YouTube", "Upload"], label_visibility="collapsed", horizontal=True)
        
        if input_method == "YouTube":
            url = st.text_input("YouTube URL", placeholder="Paste link here...")
            use_cookies = st.checkbox("Use Cookies (Fix 'Sign in')", value=True)
            if st.button("🚀 Import & Process"):
                if not url:
                    st.error("Enter URL")
                else:
                    with st.status("Importing Media...", expanded=True) as status:
                        try:
                            st.write("Downloading...")
                            audio_path, title = download_audio(url, use_cookies=use_cookies)
                            st.session_state.audio_path = audio_path
                            st.session_state.title = title
                            
                            st.write("Isolating Vocals...")
                            vocals_path = isolate_vocals(audio_path)
                            
                            st.write("Transcribing...")
                            segments = transcribe_with_lyrics(vocals_path, model_size="medium")
                            st.session_state.segments = segments
                            status.update(label="Ready to Edit!", state="complete", expanded=False)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                            status.update(label="Failed", state="error")
                            
        else:
            uploaded = st.file_uploader("Upload Audio", type=["mp3", "wav"])
            if uploaded and st.button("🚀 Process File"):
                with st.status("Processing...", expanded=True) as status:
                    temp_dir = "temp"
                    os.makedirs(temp_dir, exist_ok=True)
                    file_path = os.path.join(temp_dir, uploaded.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded.getbuffer())
                    
                    st.session_state.audio_path = file_path
                    st.session_state.title = uploaded.name
                    
                    try:
                        vocals_path = isolate_vocals(file_path)
                        segments = transcribe_with_lyrics(vocals_path, model_size="medium")
                        st.session_state.segments = segments
                        status.update(label="Ready!", state="complete", expanded=False)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    # --- 2. STYLE ---
    with st.expander("🎨 2. Design & Style", expanded=True):
        # Fonts
        st.caption("Typography")
        c1, c2 = st.columns(2)
        with c1:
            f_cat = st.selectbox("Category", list(GOOGLE_FONTS.keys()))
        with c2:
            f_name = st.selectbox("Font", list(GOOGLE_FONTS[f_cat].keys()))
            
        selected_font_path = get_font_path(f_cat, f_name)
        
        # Colors
        st.caption("Color Palette")
        c3, c4 = st.columns(2)
        
        # Background
        bg_file = st.file_uploader("Background Image", type=["png", "jpg"])
        
        # Logic for auto-color (hidden unless bg exists)
        if bg_file:
            # Auto detect
            img = Image.open(bg_file)
            stat = ImageStat.Stat(img.convert('L'))
            avg_bright = stat.mean[0]
            if st.button("🪄 Auto-Match Colors"):
                if avg_bright < 128:
                    st.session_state.color_active = "#FFE600"
                    st.session_state.color_inactive = "#E0E0E0"
                else:
                    st.session_state.color_active = "#D60000" 
                    st.session_state.color_inactive = "#333333"
                st.rerun()
        
        with c3:
            color_active = st.color_picker("Active", st.session_state.color_active)
            st.session_state.color_active = color_active
        with c4:
            color_inactive = st.color_picker("Inactive", st.session_state.color_inactive)
            st.session_state.color_inactive = color_inactive

    # --- 3. EXPORT ---
    with st.expander("📤 3. Export", expanded=True):
        if st.button("🔥 Render Video", type="primary"):
            if not st.session_state.segments:
                st.warning("No lyrics to render")
            else:
                with st.status("Rendering...", expanded=True):
                    out_name = "output_final.mp4"
                    
                    # Prepare BG
                    bg_path = "sunset_mountains_bg.png"
                    if bg_file:
                        bg_path = os.path.join("temp", bg_file.name)
                        bg_file.seek(0)
                        with open(bg_path, "wb") as f:
                            f.write(bg_file.getbuffer())
                    elif os.path.exists("default_bg_16_9.png"):
                         bg_path = "default_bg_16_9.png"
                    
                    # Colors
                    def h2rgba(h, a=255):
                        h = h.lstrip('#')
                        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)
                    
                    create_lyrics_video(
                        st.session_state.audio_path,
                        st.session_state.segments,
                        out_name,
                        bg_image_path=bg_path,
                        font_path=selected_font_path,
                        color_active=h2rgba(color_active),
                        color_inactive=h2rgba(color_inactive, 180)
                    )
                    st.session_state.video_path = out_name
                    st.success("Done!")

# --- MAIN AREA ---
# Top: Preview / Player
# Bottom: Timeline (Lyrics Editor)

st.subheader(f"Project: {st.session_state.title if st.session_state.title else 'New Project'}")

# Preview Section
col_preview, col_props = st.columns([2, 1])

with col_preview:
    if st.session_state.video_path and os.path.exists(st.session_state.video_path):
        st.video(st.session_state.video_path)
    
    if bg_file:
        st.image(bg_file, caption="Background Preview", use_container_width=True)
    elif os.path.exists("default_bg_16_9.png"):
        st.image("default_bg_16_9.png", caption="Default Background (16:9)", use_container_width=True)
    else:
        st.info("Import media to start preview")

with col_props:
    st.write("### Style Preview")
    # Live Font Preview
    if selected_font_path:
        try:
            preview_h, preview_w = 150, 400
            # Use actual bg color if possible or just dark
            preview_img = Image.new('RGBA', (preview_w, preview_h), (30, 30, 30, 255))
            draw = ImageDraw.Draw(preview_img)
            p_font = ImageFont.truetype(selected_font_path, 40)
            
            # Draw Inactive
            draw.text((20, 20), "Previous Line...", font=p_font, fill=st.session_state.color_inactive)
            # Draw Active
            draw.text((20, 70), "Current Sung Line!", font=p_font, fill=st.session_state.color_active)
            
            st.image(preview_img, use_container_width=True)
        except:
            st.warning("Font loading...")

st.divider()

# Timeline / Editor
st.write("### ✂️ Lyrics Editor")
if st.session_state.segments:
    # Prepare data
    data = []
    for i, s in enumerate(st.session_state.segments):
        data.append({
            "Start": s['start'],
            "End": s['end'],
            "Lyrics": s['text'].strip()
        })
    
    edited = st.data_editor(
        data, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "Start": st.column_config.NumberColumn(format="%.2fs"),
            "End": st.column_config.NumberColumn(format="%.2fs"),
            "Lyrics": st.column_config.TextColumn(width="large")
        }
    )
    
    if st.button("Update Timeline"):
        # Sync back
        for i, row in enumerate(edited):
            if i < len(st.session_state.segments):
                seg = st.session_state.segments[i]
                if seg['text'] != row['Lyrics']:
                    seg['text'] = row['Lyrics']
                    # Simple re-sync of words
                    words = row['Lyrics'].split()
                    dur = seg['end'] - seg['start']
                    per_word = dur / max(len(words), 1)
                    cursor = seg['start']
                    new_words = []
                    for w in words:
                        new_words.append({'word': w, 'start': cursor, 'end': cursor + per_word})
                        cursor += per_word
                    seg['words'] = new_words
        st.success("Timeline Synced")
else:
    st.info("Import a song to see the timeline editor.")
