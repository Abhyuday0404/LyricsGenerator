import os
import whisper
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ API key not found. Make sure you have a .env file with GEMINI_API_KEY=...")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def extract_vocals(audio_path):
    print("🎵 Extracting vocals using Spleeter...")
    try:
        subprocess.run([
            "spleeter", "separate", "-p", "spleeter:2stems",
            "-o", "output", audio_path
        ], check=True)
        vocals_path = os.path.join("output", os.path.splitext(os.path.basename(audio_path))[0], "vocals.wav")
        if not os.path.exists(vocals_path):
            raise FileNotFoundError("❌ Failed to extract vocals.")
        print("✅ Vocals extracted successfully.")
        return vocals_path
    except Exception as e:
        print(f"❌ Error during vocal separation: {e}")
        raise

def transcribe_audio(audio_path):
    print("📝 Transcribing audio with Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    print("✅ Transcription complete.")
    return result["text"]

def query_gemini(transcription):
    if len(transcription) > 3000:
        transcription = transcription[:3000]

    prompt = f"""
These are raw transcribed lyrics from a song. Please clean them up by:
- Adding punctuation and line breaks
- Correcting grammar and spelling
- Making it look like proper readable lyrics

Raw lyrics:
{transcription}
"""
    print("🧠 Sending to Gemini...")

    try:
        response = model.generate_content(prompt)
        print("✅ Gemini response received.")
        return response.text
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return None

def process_song(audio_path):
    vocals_path = extract_vocals(audio_path)
    transcription = transcribe_audio(vocals_path)
    cleaned_lyrics = query_gemini(transcription)

    if cleaned_lyrics:
        output_file = "cleaned_lyrics.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_lyrics)
        print(f"✅ Cleaned lyrics saved to {output_file}")
    else:
        print("⚠️ Could not process lyrics with Gemini.")

# ---------- Run ----------
if __name__ == "__main__":
    file_path = input("🎵 Enter the full path to your song file (e.g. C:/ai/song.mp3): ").strip('"')
    
    if not os.path.exists(file_path):
        print("❌ The file was not found. Please check the path and try again.")
    else:
        process_song(file_path)
