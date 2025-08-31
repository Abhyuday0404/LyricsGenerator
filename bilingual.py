import os
import subprocess
import re
import sys
from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
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

# Step 3: Offline Clean-Up
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
            
        # Capitalize English, leave Hindi as-is
        if re.search(r'[\u0900-\u097F]', content):  # Hindi
            cleaned_lines.append(f"{timestamp} {content}" if timestamp else content)
        else:
            cleaned_lines.append(f"{timestamp} {content.capitalize()}" if timestamp else content.capitalize())
    cleaned = '\n'.join(cleaned_lines)
    print("[SUCCESS] Cleaned lyrics ready.", flush=True)
    return cleaned

# Step 4: Romanize Hindi
def transliterate_lyrics(text):
    print("🔡 Romanizing Hindi lyrics (ITRANS)...")
    try:
        def transliterate_line(line):
            if re.search(r'[\u0900-\u097F]', line):
                return transliterate(line, DEVANAGARI, ITRANS).lower()
            return line
        romanized = '\n'.join([transliterate_line(l) for l in text.splitlines()])
        with open("bilingual_romanized.txt", "w", encoding="utf-8") as f:
            f.write(romanized)
        print("[SUCCESS] Romanized lyrics saved.")
        return romanized
    except Exception as e:
        print(f"[ERROR] Transliteration error: {e}")
        return None

# Step 5: Menu to choose final output
def offer_menu():
    print("\nWhich lyrics would you like to save as final output?")
    print("1. Raw Transcription (bilingual_transcribed.txt)")
    print("2. Cleaned Bilingual Lyrics (bilingual_cleaned.txt)")
    print("3. Romanized Lyrics (bilingual_romanized.txt)")
    choice = input("Enter your choice (1/2/3): ").strip()
    mapping = {
        "1": ("bilingual_transcribed.txt", "bilingual_output.txt"),
        "2": ("bilingual_cleaned.txt", "bilingual_output.txt"),
        "3": ("bilingual_romanized.txt", "bilingual_output.txt"),
    }
    if choice in mapping:
        src, dest = mapping[choice]
        if os.path.exists(src):
            with open(src, "r", encoding="utf-8") as f:
                content = f.read()
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[SUCCESS] Your selected lyrics saved as {dest}.")
        else:
            print(f"[ERROR] File {src} not found.")
    else:
        print("⚠️ Invalid choice.")

# Full pipeline
def process_bilingual_song(audio_path):
    print("\nHow do you want your lyrics?")
    print("1. Original script (Hindi in Devanagari, English as-is)")
    print("2. Romanized (Hindi in Latin/English, English as-is)")
    mode = input("Enter 1 or 2: ").strip()
    vocals_path = extract_vocals(audio_path)
    transcription = transcribe_audio(vocals_path)
    cleaned = clean_transcription(transcription)
    output = None
    if mode == "2":
        print("🔡 Romanizing Hindi lyrics (ITRANS)...")
        try:
            def transliterate_line(line):
                if re.search(r'[\u0900-\u097F]', line):
                    return transliterate(line, DEVANAGARI, ITRANS).lower()
                return line
            output = '\n'.join([transliterate_line(l) for l in cleaned.splitlines()])
            print("[SUCCESS] Romanized lyrics ready.")
        except Exception as e:
            print(f"[ERROR] Transliteration error: {e}")
            return
    else:
        output = cleaned
        print("[SUCCESS] Cleaned lyrics ready.")
    # Save only the selected output
    with open("bilingual_output.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print("[SUCCESS] Final output saved as bilingual_output.txt.")
    
    # Print the lyrics for Streamlit to capture
    print("\n" + "="*50)
    print("LYRICS OUTPUT:")
    print("="*50)
    print(output)

# ---------- Entry ----------
if __name__ == "__main__":
    # Check if audio path is provided as command line argument
    if len(sys.argv) > 1:
        # Called from Streamlit app with audio path as argument
        path = sys.argv[1]
        
        if not os.path.exists(path):
            print("[ERROR] File not found. Please check the path.")
            sys.exit(1)
        else:
            process_bilingual_song(path)
    else:
        # Interactive mode
        print("*** Bilingual Song Lyrics Processor (Offline Mode) ***")
        path = input("Enter full path of your song (e.g., C:/songs/mysong.mp3): ").strip('"')
        if not os.path.exists(path):
            print("[ERROR] File not found. Please check the path.")
        else:
            process_bilingual_song(path)
