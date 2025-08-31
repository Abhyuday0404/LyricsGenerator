# ---------------------------
import os
import subprocess
import torch
import re
import datetime
import sys
from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
from faster_whisper import WhisperModel

# -----------------------
# Utility: Colored Prints
def log_step(msg): print(f"\n[STEP] {msg}", flush=True)
def log_success(msg): print(f"[SUCCESS] {msg}", flush=True)
def log_error(msg): print(f"[ERROR] {msg}", flush=True)
def log_info(msg): print(f"[INFO] {msg}", flush=True)

# -----------------------
def get_user_choice():
    print("What output format do you want?")
    print("1. Raw Transcription (as spoken)")
    print("2. Cleaned Hindi Lyrics (formatted like a song)")
    print("3. Romanized Lyrics (Hindi in English script)")
    choice = input("Enter your choice (1/2/3): ").strip()

    return {
        "1": "raw",
        "2": "cleaned",
        "3": "romanized"
    }.get(choice)

# -----------------------
def extract_vocals(audio_path):
    log_step("STEP 1: Extracting vocals using Spleeter...")
    try:
        subprocess.run([
            "spleeter", "separate", "-p", "spleeter:2stems",
            "-o", "output", audio_path
        ], check=True)

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        vocals_path = os.path.join("output", base_name, "vocals.wav")

        if not os.path.exists(vocals_path):
            raise FileNotFoundError("Vocals file not found.")

        log_success("Vocals extracted successfully.")
        return vocals_path
    except subprocess.CalledProcessError:
        log_error("Spleeter failed. Please ensure it is installed and available in PATH.")
        exit()

# -----------------------
def transcribe_audio(audio_path):
    log_step("STEP 2: Transcribing audio with FasterWhisper...")

    model = WhisperModel(
        "medium",
        device="cuda" if torch.cuda.is_available() else "cpu",
        compute_type="float16" if torch.cuda.is_available() else "int8"
    )

    segments, info = model.transcribe(audio_path, language="hi")
    log_success(f"Transcription complete. Duration: {info.duration:.2f}s")

    lines = []
    for segment in segments:
        if segment.text.strip():
            timestamp = f"[{segment.start:.2f}-{segment.end:.2f}]"
            lines.append(f"{timestamp} {segment.text.strip()}")
    return "\n".join(lines)

# -----------------------
def clean_lyrics(text):
    log_step("STEP 3: Formatting transcription like lyrics...")
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Extract timestamp and text
        timestamp = line[:line.find(']')+1] if '[' in line else ''
        content = line[line.find(']')+1:].strip() if '[' in line else line.strip()
        
        # Clean the content while preserving timestamp
        content = re.sub(r"\s+", " ", content)
        content = re.sub(r"\b(है|हूँ|हूं|हो|था|थी|थे|हैं)\b", r"\1.", content)
        content = re.sub(r"([।.?!])", r"\1", content)
        
        if timestamp and content:
            cleaned_lines.append(f"{timestamp} {content}")
    
    return '\n'.join(cleaned_lines)

# -----------------------
def transliterate_lyrics(text):
    log_step("STEP 4: Romanizing lyrics...")
    return transliterate(text, DEVANAGARI, ITRANS).lower()

# -----------------------
def save_output(text, output_type):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lyrics_{output_type}_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text.strip())
    log_success(f"Final output saved to {filename}")

# -----------------------
def process_song(audio_path, output_type):
    log_info(f"Starting conversion for: {output_type.upper()}")
    vocals = extract_vocals(audio_path)
    transcription = transcribe_audio(vocals)

    final_output = ""
    if output_type == "raw":
        final_output = transcription
        save_output(transcription, output_type)
    elif output_type == "cleaned":
        cleaned = clean_lyrics(transcription)
        final_output = cleaned
        save_output(cleaned, output_type)
    elif output_type == "romanized":
        cleaned = clean_lyrics(transcription)
        romanized = transliterate_lyrics(cleaned)
        final_output = romanized
        save_output(romanized, output_type)
    else:
        log_error("Unknown output type selected.")
        return
    
    # Print the lyrics for Streamlit to capture
    print("\n" + "="*50)
    print("LYRICS OUTPUT:")
    print("="*50)
    print(final_output)

# -----------------------
if __name__ == "__main__":
    # Check if audio path is provided as command line argument
    if len(sys.argv) > 1:
        # Called from Streamlit app with audio path as argument
        path = sys.argv[1]
        output_type = "cleaned"  # Default to cleaned lyrics for Streamlit
        
        if not os.path.exists(path):
            log_error("File not found. Please check the path.")
            sys.exit(1)
        else:
            process_song(path, output_type)
    else:
        # Interactive mode
        print("*** Hindi Song Lyrics Processor (Offline) ***")
        output_type = get_user_choice()

        if not output_type:
            log_error("Invalid selection. Please choose 1, 2, or 3.")
            exit()

        path = input("Enter full path of your Hindi song (e.g., C:/songs/mysong.mp3): ").strip('"')

        if not os.path.exists(path):
            log_error("File not found. Please check the path.")
        else:
            process_song(path, output_type)
