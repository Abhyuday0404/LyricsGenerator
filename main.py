import os
import subprocess
import re
from faster_whisper import WhisperModel
import torch

# Step 1: Spleeter - Extract Vocals
def extract_vocals(audio_path):
    print("🎵 Extracting vocals using Spleeter...")
    subprocess.run([
        "spleeter", "separate", "-p", "spleeter:2stems",
        "-o", "output", audio_path
    ], check=True)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    vocals_path = os.path.join("output", base_name, "vocals.wav")
    if not os.path.exists(vocals_path):
        raise FileNotFoundError("❌ Vocals file not found.")
    print("✅ Vocals extracted.")
    return vocals_path

# Step 2: FasterWhisper - Transcribe
def transcribe_audio(audio_path):
    print("📝 Transcribing with FasterWhisper...")
    model = WhisperModel("large-v2", device="cuda" if torch.cuda.is_available() else "cpu", compute_type="float16" if torch.cuda.is_available() else "int8")
    segments, info = model.transcribe(audio_path)
    print(f"✅ Transcription complete. Duration: {info.duration:.2f}s")
    text = ""
    for segment in segments:
        text += segment.text.strip() + "\n"
    return text.strip()

# Step 3: Offline Clean-Up (English only)
def clean_transcription(text):
    print("🧹 Cleaning transcription (offline)...")
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Capitalize English text
        cleaned_lines.append(line.capitalize())
    cleaned = '\n'.join(cleaned_lines)
    print("✅ Cleaned lyrics ready.")
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
    print(f"✅ Cleaned English lyrics saved to {output_file}")

# ---------- Entry ----------
if __name__ == "__main__":
    print("🎤 English Song Lyrics Processor (Offline Mode)")
    file_path = input("📂 Enter the full path to your song file (e.g., C:/ai/song.mp3): ").strip('"')
    
    if not os.path.exists(file_path):
        print("❌ The file was not found. Please check the path and try again.")
    else:
        process_song(file_path)
