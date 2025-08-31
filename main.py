import os
import subprocess
import re
import sys
from faster_whisper import WhisperModel
import torch

# Step 1: Spleeter - Extract Vocals
def extract_vocals(audio_path):
    print("[INFO] Extracting vocals using Spleeter...", flush=True)
    subprocess.run([
        "spleeter", "separate", "-p", "spleeter:2stems",
        "-o", "output", audio_path
    ], check=True)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    vocals_path = os.path.join("output", base_name, "vocals.wav")
    if not os.path.exists(vocals_path):
        raise FileNotFoundError("[ERROR] Vocals file not found.")
    print("[SUCCESS] Vocals extracted.", flush=True)
    return vocals_path

# Step 2: FasterWhisper - Transcribe
def transcribe_audio(audio_path):
    print("[INFO] Transcribing with FasterWhisper...", flush=True)
    model = WhisperModel("large-v2", device="cuda" if torch.cuda.is_available() else "cpu", compute_type="float16" if torch.cuda.is_available() else "int8")
    segments, info = model.transcribe(audio_path)
    print(f"[SUCCESS] Transcription complete. Duration: {info.duration:.2f}s", flush=True)
    text = ""
    for segment in segments:
        timestamp = f"[{segment.start:.2f}-{segment.end:.2f}]"
        text += f"{timestamp} {segment.text.strip()}\n"
    return text.strip()

# Step 3: Offline Clean-Up (English only)
def clean_transcription(text):
    print("[INFO] Cleaning transcription (offline)...", flush=True)
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
            
        # Extract timestamp if present
        timestamp = ""
        content = line
        if line.startswith("[") and "]" in line:
            timestamp = line[:line.find("]")+1]
            content = line[line.find("]")+1:].strip()
            
        # Capitalize English text
        cleaned_lines.append(f"{timestamp} {content.capitalize()}" if timestamp else content.capitalize())
    cleaned = '\n'.join(cleaned_lines)
    print("[SUCCESS] Cleaned lyrics ready.", flush=True)
    return cleaned

# Full pipeline for English songs
def process_song(audio_path):
    vocals_path = extract_vocals(audio_path)
    transcription = transcribe_audio(vocals_path)
    cleaned_lyrics = clean_transcription(transcription)
    
    # Save the cleaned lyrics
    output_file = "english_lyrics.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned_lyrics)
    print(f"[SUCCESS] Cleaned English lyrics saved to {output_file}", flush=True)
    
    # Print the lyrics for Streamlit to capture
    print("\n" + "="*50)
    print("LYRICS OUTPUT:")
    print("="*50)
    print(cleaned_lyrics)

# ---------- Entry ----------
if __name__ == "__main__":
    # Check if audio path is provided as command line argument
    if len(sys.argv) > 1:
        # Called from Streamlit app with audio path as argument
        file_path = sys.argv[1]
        
        if not os.path.exists(file_path):
            print("[ERROR] The file was not found. Please check the path and try again.")
            sys.exit(1)
        else:
            process_song(file_path)
    else:
        # Interactive mode
        print("*** English Song Lyrics Processor (Offline Mode) ***")
        file_path = input("Enter the full path to your song file (e.g., C:/ai/song.mp3): ").strip('"')
        
        if not os.path.exists(file_path):
            print("[ERROR] The file was not found. Please check the path and try again.")
        else:
            process_song(file_path)
