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

# Full pipeline for songs with fallback to Gemini API
def process_song(audio_path, use_gemini=False):
    vocals_path = extract_vocals(audio_path)
    
    if use_gemini:
        # Import and use hindiapi for Gemini-powered translation
        try:
            from hindiapi import transcribe_audio as gemini_transcribe
            transcription = gemini_transcribe(vocals_path)
        except ImportError:
            print("[ERROR] Could not import hindiapi. Make sure GEMINI_API_KEY is set in .env", flush=True)
            return None
    else:
        # Use regular transcription
        transcription = transcribe_audio(vocals_path)
    
    cleaned_lyrics = clean_transcription(transcription)
    
    # Save the cleaned lyrics
    output_file = "lyrics_output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned_lyrics)
    print(f"[SUCCESS] Cleaned lyrics saved to {output_file}", flush=True)
    
    # Print the lyrics for Streamlit to capture
    print("\n" + "="*50)
    print("LYRICS OUTPUT:")
    print("="*50)
    print(cleaned_lyrics)
    
    return cleaned_lyrics

# ---------- Entry ----------
if __name__ == "__main__":
    # Check if audio path is provided as command line argument
    if len(sys.argv) > 1:
        # Called from Streamlit app with audio path as argument
        file_path = sys.argv[1]
        use_gemini = len(sys.argv) > 2 and sys.argv[2].lower() == "gemini"
        
        if not os.path.exists(file_path):
            print("[ERROR] The file was not found. Please check the path and try again.")
            sys.exit(1)
        else:
            lyrics = process_song(file_path, use_gemini)
            if not use_gemini:
                print("\nAre you satisfied with the translation? (yes/no)")
                feedback = input().strip().lower()
                if feedback == "no":
                    print("\n[INFO] Trying with Gemini API for better translation...", flush=True)
                    process_song(file_path, use_gemini=True)
    else:
        # Interactive mode
        print("*** Song Lyrics Processor ***")
        file_path = input("Enter the full path to your song file (e.g., C:/ai/song.mp3): ").strip('"')
        
        if not os.path.exists(file_path):
            print("[ERROR] The file was not found. Please check the path and try again.")
        else:
            lyrics = process_song(file_path)
            print("\nAre you satisfied with the translation? (yes/no)")
            feedback = input().strip().lower()
            if feedback == "no":
                print("\n[INFO] Trying with Gemini API for better translation...", flush=True)
                process_song(file_path, use_gemini=True)
