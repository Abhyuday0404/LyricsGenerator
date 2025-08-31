# 🎵 AI-Powered Lyrics Transcription Studio
An interactive web application that automatically transcribes song lyrics from an audio file. 
This tool separates vocals from the music and uses advanced AI models to generate accurate, timestamped lyrics for English, Hindi, and Bilingual songs.
✨ Key Features

🎤 Vocal Separation: Automatically isolates vocals from background music using Spleeter for clearer transcription.
🌐 Multi-Language Support: High-accuracy transcription for:
  - English
  - Hindi (Devanagari script)
  - Bilingual (Hindi + English)
🚀 High-Performance AI: Powered by `faster-whisper` for speedy and precise transcription, with GPU support.
📝 Multiple Output Formats:
  - Cleaned Lyrics: Formatted with proper capitalization and punctuation.
  - Romanized Hindi: Transliterates Devanagari script into Latin (English) characters for easier reading.
💻 Interactive Web UI: A user-friendly interface built with Streamlit that provides real-time progress updates.
🧠 AI-Enhanced Formatting (Optional):** Use the Google Gemini API to intelligently clean and format Hindi lyrics for superior punctuation and readability.



🛠️ Technology Stack

- Backend: Python
- Frontend: Streamlit
- Vocal Separation: Spleeter
- Transcription: `faster-whisper` (an optimized implementation of OpenAI's Whisper model)

- Transliteration: `indic-transliteration`

