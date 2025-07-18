import os
import sys
import torch
from spleeter.separator import Separator
from faster_whisper import WhisperModel

def extract_vocals(input_path):
    separator = Separator('spleeter:2stems')
    output_dir = "output"
    separator.separate_to_file(input_path, output_dir)
    
    filename = os.path.splitext(os.path.basename(input_path))[0]
    vocals_path = os.path.join(output_dir, filename, 'vocals.wav')
    
    if not os.path.exists(vocals_path):
        sys.exit(1)
    return vocals_path

def transcribe_audio(vocals_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if torch.cuda.is_available() else "int8"
    
    model = WhisperModel("medium", device=device, compute_type=compute_type)
    segments, _ = model.transcribe(vocals_path, language="hi")
    
    transcription = ""
    for segment in segments:
        transcription += segment.text.strip() + " "
    
    return transcription.strip()

def main():
    input_path = input().strip('"')

    if not os.path.exists(input_path):
        sys.exit(1)

    vocals_path = extract_vocals(input_path)
    text = transcribe_audio(vocals_path)

    with open("hindi1withoutapi.txt", "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    main()
