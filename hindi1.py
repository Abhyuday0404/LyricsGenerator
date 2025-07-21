# import os
# import sys
# import torch
# from spleeter.separator import Separator
# from faster_whisper import WhisperModel

# def extract_vocals(input_path):
#     separator = Separator('spleeter:2stems')
#     output_dir = "output"
#     separator.separate_to_file(input_path, output_dir)
    
#     filename = os.path.splitext(os.path.basename(input_path))[0]
#     vocals_path = os.path.join(output_dir, filename, 'vocals.wav')
    
#     if not os.path.exists(vocals_path):
#         sys.exit(1)
#     return vocals_path

# def transcribe_audio(vocals_path):
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     compute_type = "float16" if torch.cuda.is_available() else "int8"
    
#     model = WhisperModel("medium", device=device, compute_type=compute_type)
#     segments, _ = model.transcribe(vocals_path, language="hi")
    
#     transcription = ""
#     for segment in segments:
#         transcription += segment.text.strip() + " "
    
#     return transcription.strip()

# def main():
#     input_path = input().strip('"')

#     if not os.path.exists(input_path):
#         sys.exit(1)

#     vocals_path = extract_vocals(input_path)
#     text = transcribe_audio(vocals_path)

#     with open("hindi1withoutapi.txt", "w", encoding="utf-8") as f:
#         f.write(text)

# if __name__ == "__main__":
#     main()


# import os
# import sys
# import torch
# from spleeter.separator import Separator
# from faster_whisper import WhisperModel

# def extract_vocals(input_path):
#     separator = Separator('spleeter:2stems')
#     output_dir = "output"
#     separator.separate_to_file(input_path, output_dir)
    
#     filename = os.path.splitext(os.path.basename(input_path))[0]
#     vocals_path = os.path.join(output_dir, filename, 'vocals.wav')
    
#     if not os.path.exists(vocals_path):
#         print("❌ Vocals file not found after separation.")
#         sys.exit(1)
    
#     return vocals_path

# def transcribe_audio(vocals_path):
#     if not torch.cuda.is_available():
#         raise SystemExit("❌ CUDA GPU not available. Please check your NVIDIA drivers and PyTorch installation.")

#     print("✅ Using GPU:", torch.cuda.get_device_name(0))
    
#     device = "cuda"
#     compute_type = "float16"  # Good balance between speed and precision

#     model = WhisperModel("medium", device=device, compute_type=compute_type)
#     segments, _ = model.transcribe(vocals_path, language="hi")

#     transcription = ""
#     for segment in segments:
#         transcription += segment.text.strip() + " "

#     return transcription.strip()

# def main():
#     input_path = input("🎵 Enter path to the input audio file: ").strip('"')

#     if not os.path.exists(input_path):
#         print("❌ Input file does not exist.")
#         sys.exit(1)

#     vocals_path = extract_vocals(input_path)
#     text = transcribe_audio(vocals_path)

#     output_file = "hindi1withoutapi.txt"
#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write(text)

#     print(f"✅ Transcription complete. Saved to: {output_file}")

# if __name__ == "__main__":
#     main()


# ---------------------
# import os
# import subprocess
# import torch
# import re
# from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
# from faster_whisper import WhisperModel

# # Ask user choice FIRST
# def get_user_choice():
#     print("🧾 What output format do you want?")
#     print("1️⃣  Raw Transcription (as spoken)")
#     print("2️⃣  Cleaned Hindi Lyrics (formatted like a song)")
#     print("3️⃣  Romanized Lyrics (Hindi in English script)")
#     choice = input("👉 Enter your choice (1/2/3): ").strip()

#     choices = {
#         "1": "raw",
#         "2": "cleaned",
#         "3": "romanized"
#     }
#     return choices.get(choice)

# # STEP 1: Extract vocals
# def extract_vocals(audio_path):
#     print("\n🟢 STEP 1: Extracting vocals using Spleeter...")
#     subprocess.run([
#         "spleeter", "separate", "-p", "spleeter:2stems",
#         "-o", "output", audio_path
#     ], check=True)

#     base_name = os.path.splitext(os.path.basename(audio_path))[0]
#     vocals_path = os.path.join("output", base_name, "vocals.wav")

#     if not os.path.exists(vocals_path):
#         raise FileNotFoundError("❌ Vocals file not found.")

#     print("✅ Vocals extracted successfully.")
#     return vocals_path

# # STEP 2: Transcribe
# def transcribe_audio(audio_path):
#     print("\n🟢 STEP 2: Transcribing audio with FasterWhisper...")
#     model = WhisperModel("medium", 
#                          device="cuda" if torch.cuda.is_available() else "cpu", 
#                          compute_type="float16" if torch.cuda.is_available() else "int8")

#     segments, info = model.transcribe(audio_path, language="hi")
#     print(f"✅ Transcription complete. Duration: {info.duration:.2f}s")

#     lines = [segment.text.strip() for segment in segments if segment.text.strip()]
#     final_text = "\n".join(lines)

#     return final_text

# # STEP 3: Clean Lyrics with basic formatting
# def clean_lyrics(text):
#     print("\n🟢 STEP 3: Formatting transcription like lyrics...")
#     text = re.sub(r"\s+", " ", text).strip()

#     # Add line breaks after some Hindi sentence endings (simple heuristic)
#     text = re.sub(r"\b(है|हूं|हो|था|थी|थे|हैं)\b", r"\1.\n", text)
#     # Add line breaks after punctuation
#     text = re.sub(r"([।.?!])", r"\1\n", text)
#     text = re.sub(r'\n+', '\n', text)  # Remove extra newlines

#     return text.strip()

# # STEP 4: Transliterate to Roman script
# def transliterate_lyrics(text):
#     print("\n🟢 STEP 4: Romanizing lyrics...")
#     romanized = transliterate(text, DEVANAGARI, ITRANS).lower()
#     return romanized

# # FINAL OUTPUT
# def save_output(text):
#     with open("final_output.txt", "w", encoding="utf-8") as f:
#         f.write(text.strip())
#     print("\n✅ Final output saved to final_output.txt.")

# # COMPLETE PIPELINE
# def process_song(audio_path, output_type):
#     print("\n🔄 Starting conversion for:", output_type.upper())
#     vocals = extract_vocals(audio_path)
#     transcription = transcribe_audio(vocals)

#     if output_type == "raw":
#         save_output(transcription)

#     elif output_type == "cleaned":
#         cleaned = clean_lyrics(transcription)
#         save_output(cleaned)

#     elif output_type == "romanized":
#         cleaned = clean_lyrics(transcription)
#         romanized = transliterate_lyrics(cleaned)
#         save_output(romanized)

#     else:
#         print("⚠️ Unknown output type selected.")

# # ---------- ENTRY POINT ----------
# if __name__ == "__main__":
#     print("🎤 Hindi Song Lyrics Processor (Offline & Clean Output)")

#     output_type = get_user_choice()
#     if not output_type:
#         print("❌ Invalid selection. Please choose 1, 2, or 3.")
#         exit()

#     path = input("📂 Enter full path of your Hindi song (e.g., C:/songs/mysong.mp3): ").strip('"')
#     if not os.path.exists(path):
#         print("❌ File not found. Please check the path.")
#     else:
#         process_song(path, output_type)


# ---------------------------
import os
import subprocess
import torch
import re
import datetime
from indic_transliteration.sanscript import transliterate, DEVANAGARI, ITRANS
from faster_whisper import WhisperModel

# -----------------------
# Utility: Colored Prints
def log_step(msg): print(f"\n🟢 {msg}")
def log_success(msg): print(f"✅ {msg}")
def log_error(msg): print(f"❌ {msg}")
def log_info(msg): print(f"🔹 {msg}")

# -----------------------
def get_user_choice():
    print("🧾 What output format do you want?")
    print("1️⃣  Raw Transcription (as spoken)")
    print("2️⃣  Cleaned Hindi Lyrics (formatted like a song)")
    print("3️⃣  Romanized Lyrics (Hindi in English script)")
    choice = input("👉 Enter your choice (1/2/3): ").strip()

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

    lines = [segment.text.strip() for segment in segments if segment.text.strip()]
    return "\n".join(lines)

# -----------------------
def clean_lyrics(text):
    log_step("STEP 3: Formatting transcription like lyrics...")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\b(है|हूँ|हूं|हो|था|थी|थे|हैं)\b", r"\1.\n", text)
    text = re.sub(r"([।.?!])", r"\1\n", text)
    return re.sub(r'\n+', '\n', text).strip()

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
    log_info(f"🎶 Starting conversion for: {output_type.upper()}")
    vocals = extract_vocals(audio_path)
    transcription = transcribe_audio(vocals)

    if output_type == "raw":
        save_output(transcription, output_type)
    elif output_type == "cleaned":
        cleaned = clean_lyrics(transcription)
        save_output(cleaned, output_type)
    elif output_type == "romanized":
        cleaned = clean_lyrics(transcription)
        romanized = transliterate_lyrics(cleaned)
        save_output(romanized, output_type)
    else:
        log_error("Unknown output type selected.")

# -----------------------
if __name__ == "__main__":
    print("🎤 Hindi Song Lyrics Processor (Offline)")
    output_type = get_user_choice()

    if not output_type:
        log_error("Invalid selection. Please choose 1, 2, or 3.")
        exit()

    path = input("📂 Enter full path of your Hindi song (e.g., C:/songs/mysong.mp3): ").strip('"')

    if not os.path.exists(path):
        log_error("File not found. Please check the path.")
    else:
        process_song(path, output_type)
