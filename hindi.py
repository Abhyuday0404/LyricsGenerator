# import os
# import whisper
# import subprocess
# from dotenv import load_dotenv
# import google.generativeai as genai
# from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS

# # Load Gemini API key
# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")

# if not API_KEY:
#     raise ValueError("❌ API key not found. Set GEMINI_API_KEY in your .env file.")

# # Configure Gemini
# genai.configure(api_key=API_KEY)
# gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# # Step 1: Spleeter - Extract Vocals
# def extract_vocals(audio_path):
#     print("🎵 Extracting vocals using Spleeter...")
#     subprocess.run([
#         "spleeter", "separate", "-p", "spleeter:2stems",
#         "-o", "output", audio_path
#     ], check=True)

#     base_name = os.path.splitext(os.path.basename(audio_path))[0]
#     vocals_path = os.path.join("output", base_name, "vocals.wav")

#     if not os.path.exists(vocals_path):
#         raise FileNotFoundError("❌ Vocals file not found.")

#     print("✅ Vocals extracted.")
#     return vocals_path

# # Step 2: Whisper - Transcribe
# def transcribe_audio(audio_path):
#     print("📝 Transcribing with Whisper...")
#     model = whisper.load_model("medium")
#     result = model.transcribe(audio_path, language="hi")
#     text = result["text"]
#     print("✅ Transcription done.")

#     with open("lyrics_transcribed.txt", "w", encoding="utf-8") as f:
#         f.write(text)

#     return text

# # Step 3: Gemini - Clean Lyrics
# def clean_with_gemini(text):
#     prompt = f"""
# These are raw Hindi song lyrics transcribed from audio.
# Your task is to:
# - Add punctuation (commas, periods)
# - Add line breaks to separate lyric phrases
# - Make them readable
# - Keep them in Hindi

# Raw Lyrics:
# {text}

# Cleaned and formatted lyrics:
# """
#     print("🧠 Cleaning lyrics using Gemini...")
#     try:
#         response = gemini_model.generate_content(prompt)
#         cleaned = response.text.strip()
#         with open("lyrics_cleaned.txt", "w", encoding="utf-8") as f:
#             f.write(cleaned)
#         print("✅ Cleaned lyrics saved.")
#         return cleaned
#     except Exception as e:
#         print(f"❌ Gemini error: {e}")
#         return None

# # Step 4: Transliterate - Indic Transliteration
# def transliterate_lyrics(text):
#     print("🔡 Romanizing lyrics (ITRANS)...")
#     try:
#         romanized = transliterate(text, DEVANAGARI, ITRANS)
#         with open("lyrics_romanized.txt", "w", encoding="utf-8") as f:
#             f.write(romanized)
#         print("✅ Romanized lyrics saved.")
#         return romanized
#     except Exception as e:
#         print(f"❌ Transliteration error: {e}")
#         return None

# # Step 5: Ask user which lyrics to save
# def offer_menu():
#     print("\n🧾 Which lyrics would you like to save as final output?")
#     print("1. Raw Transcription (lyrics_transcribed.txt)")
#     print("2. Cleaned Hindi Lyrics (lyrics_cleaned.txt)")
#     print("3. Romanized Lyrics (lyrics_romanized.txt)")
#     choice = input("Enter your choice (1/2/3): ").strip()

#     mapping = {
#         "1": ("lyrics_transcribed.txt", "final_output.txt"),
#         "2": ("lyrics_cleaned.txt", "final_output.txt"),
#         "3": ("lyrics_romanized.txt", "final_output.txt"),
#     }

#     if choice in mapping:
#         src, dest = mapping[choice]
#         if os.path.exists(src):
#             with open(src, "r", encoding="utf-8") as f:
#                 content = f.read()
#             with open(dest, "w", encoding="utf-8") as f:
#                 f.write(content)
#             print(f"✅ Your selected lyrics saved as {dest}.")
#         else:
#             print(f"❌ File {src} not found.")
#     else:
#         print("⚠️ Invalid choice.")

# # Full pipeline
# def process_hindi_song(audio_path):
#     vocals_path = extract_vocals(audio_path)
#     transcription = transcribe_audio(vocals_path)
#     cleaned = clean_with_gemini(transcription)
#     if cleaned:
#         transliterate_lyrics(cleaned)
#     offer_menu()

# # ---------- Entry ----------
# if __name__ == "__main__":
#     print("🎤 Hindi Song Lyrics Processor Started")
#     path = input("📂 Enter full path of your Hindi song (e.g., C:/songs/mysong.mp3): ").strip('"')
#     if not os.path.exists(path):
#         print("❌ File not found. Please check the path.")
#     else:
#         process_hindi_song(path)

# ..........................................................

import os
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai
from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
from faster_whisper import WhisperModel
import torch

# Load Gemini API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ API key not found. Set GEMINI_API_KEY in your .env file.")

# Configure Gemini
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

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
    
    # Load FasterWhisper model - use "medium" or "large-v2" for better accuracy
    model = WhisperModel("medium", device="cuda" if torch.cuda.is_available() else "cpu", compute_type="float16" if torch.cuda.is_available() else "int8")

    segments, info = model.transcribe(audio_path, language="hi")
    print(f"✅ Transcription complete. Duration: {info.duration:.2f}s")

    text = ""
    for segment in segments:
        text += segment.text.strip() + " "

    with open("lyrics_transcribed.txt", "w", encoding="utf-8") as f:
        f.write(text.strip())

    return text.strip()

# Step 3: Gemini - Clean Lyrics
def clean_with_gemini(text):
    prompt = f"""
These are raw Hindi song lyrics transcribed from audio.
Your task is to:
- Add punctuation (commas, periods)
- Add line breaks to separate lyric phrases
- Make them readable
- Keep them in Hindi

Raw Lyrics:
{text}

Cleaned and formatted lyrics:
"""
    print("🧠 Cleaning lyrics using Gemini...")
    try:
        response = gemini_model.generate_content(prompt)
        cleaned = response.text.strip()
        with open("lyrics_cleaned.txt", "w", encoding="utf-8") as f:
            f.write(cleaned)
        print("✅ Cleaned lyrics saved.")
        return cleaned
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return None

# Step 4: Transliterate - Indic Transliteration
def transliterate_lyrics(text):
    print("🔡 Romanizing lyrics (ITRANS)...")
    try:
        romanized = transliterate(text, DEVANAGARI, ITRANS)
        with open("lyrics_romanized.txt", "w", encoding="utf-8") as f:
            f.write(romanized)
        print("✅ Romanized lyrics saved.")
        return romanized
    except Exception as e:
        print(f"❌ Transliteration error: {e}")
        return None

# Step 5: Ask user which lyrics to save
def offer_menu():
    print("\n🧾 Which lyrics would you like to save as final output?")
    print("1. Raw Transcription (lyrics_transcribed.txt)")
    print("2. Cleaned Hindi Lyrics (lyrics_cleaned.txt)")
    print("3. Romanized Lyrics (lyrics_romanized.txt)")
    choice = input("Enter your choice (1/2/3): ").strip()

    mapping = {
        "1": ("lyrics_transcribed.txt", "final_output.txt"),
        "2": ("lyrics_cleaned.txt", "final_output.txt"),
        "3": ("lyrics_romanized.txt", "final_output.txt"),
    }

    if choice in mapping:
        src, dest = mapping[choice]
        if os.path.exists(src):
            with open(src, "r", encoding="utf-8") as f:
                content = f.read()
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Your selected lyrics saved as {dest}.")
        else:
            print(f"❌ File {src} not found.")
    else:
        print("⚠️ Invalid choice.")

# Full pipeline
def process_hindi_song(audio_path):
    vocals_path = extract_vocals(audio_path)
    transcription = transcribe_audio(vocals_path)
    cleaned = clean_with_gemini(transcription)
    if cleaned:
        transliterate_lyrics(cleaned)
    offer_menu()

# ---------- Entry ----------
if __name__ == "__main__":
    print("🎤 Hindi Song Lyrics Processor Started")
    path = input("📂 Enter full path of your Hindi song (e.g., C:/songs/mysong.mp3): ").strip('"')
    if not os.path.exists(path):
        print("❌ File not found. Please check the path.")
    else:
        process_hindi_song(path)


