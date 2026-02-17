# 🎬 GenLyrics Studio

A local AI tool that generates lyrics videos from any song.
It uses **Demucs** to isolate vocals and **OpenAI Whisper** for word-level transcription, wrapping it all in a **Streamlit** GUI.

![App Screenshot](default_bg_16_9.png)

## ✨ Features

*   **🎵 Source Flexibility**: Paste a **YouTube Link** or **Upload** your own MP3/WAV.
*   **🧠 AI Processing**:
    *   **Demucs**: Separates vocals from the instrumental.
    *   **Whisper**: Generates word-level timestamps.
*   **🎨 Split-Screen UI**:
    *   Dark Mode interface.
    *   Tools on left, Preview on right.
    *   **Auto-Color Detection**: Analyzes your background image and suggests text colors (Gold/White vs Red/Black) for readability.
*   **✍️ Full Control**:
    *   **Lyrics Editor**: Edit text and timing in a table view.
    *   **Design**: Choose from Google Fonts and custom backgrounds.
*   **⚡️ Efficient Rendering**: Outputs 1080p video.

## 🛠️ Installation

1.  **Clone the repo**
    ```bash
    git clone https://github.com/irfanripat/genlyrics-studio.git
    cd genlyrics-studio
    ```

2.  **Create a Virtual Environment** (Recommended)
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install FFmpeg** (Required for audio processing)
    *   **Mac**: `brew install ffmpeg`
    *   **Windows**: [Download here](https://ffmpeg.org/download.html)
    *   **Linux**: `sudo apt install ffmpeg`

## 🚀 Usage

Run the app locally:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

## 🏗️ How it Works

1.  **Download**: Fetches audio from YouTube or Local File.
2.  **Separate**: Uses `Demucs` to split the track into `vocals.wav` and `no_vocals.wav`.
3.  **Transcribe**: `Whisper` listens *only* to the vocals to get accurate lyrics and timestamps.
4.  **Render**: The custom renderer draws the text frame-by-frame using `Pillow` (for high-quality typography) and `OpenCV` (for video encoding).

## 📄 License

MIT License. Feel free to fork and modify!
