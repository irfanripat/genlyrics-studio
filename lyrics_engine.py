import whisper
import warnings

# Suppress FP16 warning on CPU
warnings.filterwarnings("ignore")

def transcribe_with_lyrics(audio_path, model_size="small"):
    """
    Transcribes audio and returns segments with WORD-level timestamps.
    """
    print(f"Transcribing {audio_path} using Whisper ({model_size})...")
    
    model = whisper.load_model(model_size)
    
    # word_timestamps=True is crucial here
    result = model.transcribe(audio_path, word_timestamps=True)
    
    return result['segments']

def isolate_vocals(audio_path, output_dir="./temp/separated"):
    """
    Uses demucs (installed in venv-demucs-sys) to separate vocals.
    Returns path to vocals.wav.
    """
    import subprocess
    import glob
    import os
    
    print(f"Isolating vocals for {audio_path}...")
    
    # Path to the python executable in the venv we created
    demucs_python = "./venv-demucs-sys/bin/python3"
    
    # Run demucs module
    # -n htdemucs: High quality, fast
    cmd = [demucs_python, "-m", "demucs", "-n", "htdemucs", "--two-stems=vocals", "-o", output_dir, audio_path]
    
    try:
        subprocess.run(cmd, check=True)
        
        # Find the output file
        # Structure: output_dir/htdemucs/song_name/vocals.wav
        song_name = os.path.splitext(os.path.basename(audio_path))[0]
        vocals_path = os.path.join(output_dir, "htdemucs", song_name, "vocals.wav")
        
        if os.path.exists(vocals_path):
            print(f"Vocals isolated: {vocals_path}")
            return vocals_path
        else:
            print("Could not find vocals output. Returning original.")
            return audio_path
            
    except Exception as e:
        print(f"Demucs failed: {e}. Using original audio.")
        return audio_path

