import streamlit as st
import subprocess
import os
import base64
import time

# Set page config for better appearance
st.set_page_config(
    page_title="🎵 Lyrics Transcription App",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

def run_backend_script(script_name, audio_path, use_gemini=False):
    """Runs the specified backend script and returns the output."""
    try:
        # Set environment variable to handle Unicode properly on Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Create progress bar and status
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Prepare command with optional Gemini flag
        command = ["python", script_name, audio_path]
        if use_gemini:
            command.append("gemini")
        
        # Start the subprocess with streaming output
        process = subprocess.Popen(
            ["python", script_name, audio_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            encoding='utf-8',
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        output_text = ""
        progress_steps = {
            "[INFO] Extracting vocals": 25,
            "[SUCCESS] Vocals extracted": 40,
            "[INFO] Transcribing": 50,
            "[SUCCESS] Transcription complete": 80,
            "[INFO] Cleaning": 90,
            "[SUCCESS] Cleaned lyrics ready": 95,
            "[SUCCESS] Cleaned English lyrics saved": 100
        }
        
        current_progress = 0
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                output_text += output
                
                # Update progress based on output
                for key, progress_value in progress_steps.items():
                    if key in output and progress_value > current_progress:
                        current_progress = progress_value
                        progress_bar.progress(current_progress)
                        if "Extracting vocals" in key:
                            status_text.info("🎵 Extracting vocals from audio...")
                        elif "Vocals extracted" in key:
                            status_text.success("✅ Vocals extracted successfully!")
                        elif "Transcribing" in key:
                            status_text.info("🎙️ Transcribing audio to text...")
                        elif "Transcription complete" in key:
                            status_text.success("✅ Transcription completed!")
                        elif "Cleaning" in key:
                            status_text.info("🧹 Cleaning and formatting lyrics...")
                        elif "Cleaned lyrics ready" in key:
                            status_text.success("✅ Lyrics processed successfully!")
                        elif "saved" in key:
                            status_text.success("💾 Lyrics saved! Ready for download.")
                        break
        
        # Wait for process to complete
        return_code = process.poll()
        
        # Get any remaining output
        remaining_stdout, stderr = process.communicate()
        if remaining_stdout:
            output_text += remaining_stdout
        
        if return_code != 0:
            st.error(f"❌ Processing failed: {stderr}")
            return None
        
        # Complete the progress bar
        progress_bar.progress(100)
        status_text.success("🎉 Processing completed successfully!")
        
        return output_text
        
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        return None

def get_binary_file_downloader_html(bin_str, file_ext, file_name):
    """Generates a link allowing the data in bin_str to be downloaded."""
    b64 = base64.b64encode(bin_str.encode()).decode()
    href = f'<a href="data:file/{file_ext};base64,{b64}" download="{file_name}.{file_ext}">Download {file_name}</a>'
    return href

def create_download_button(lyrics_content, filename):
    """Creates a styled download button for lyrics"""
    if lyrics_content:
        # Extract just the lyrics content (remove log messages)
        lines = lyrics_content.split('\n')
        clean_lyrics = []
        for line in lines:
            # Skip log messages and system output
            if not any(marker in line for marker in ['[INFO]', '[SUCCESS]', '[ERROR]', 'INFO:spleeter']):
                clean_line = line.strip()
                if clean_line and not clean_line.startswith('='):
                    clean_lyrics.append(clean_line)
        
        final_lyrics = '\n'.join(clean_lyrics)
        
        if final_lyrics:
            st.download_button(
                label="📥 Download Lyrics",
                data=final_lyrics,
                file_name=f"{filename}.txt",
                mime="text/plain",
                key=f"download_{filename}",
                help="Click to download the transcribed lyrics"
            )
            return True
    return False

def main():
    # Header with gradient background
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 3rem;">
            🎵 Lyrics Transcription Studio
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Transform your audio into beautiful lyrics with AI-powered transcription
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for additional info
    with st.sidebar:
        st.markdown("### 🎯 How it works")
        st.markdown("""
        1. **Upload** your audio file
        2. **Select** the language
        3. **Wait** for AI magic ✨
        4. **Download** your lyrics!
        """)
        
        st.markdown("### 📋 Supported Formats")
        st.markdown("• MP3, WAV, OGG, FLAC")
        
        st.markdown("### 🌟 Features")
        st.markdown("""
        • Real-time progress tracking
        • Multi-language support
        • High-quality transcription
        • Clean lyrics formatting
        """)

    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Language selection with custom styling
        st.markdown("### 🌐 Select Language")
        option = st.selectbox(
            "",
            ("Choose option", "Hindi", "English", "Bilingual"),
            help="Select the primary language of your audio file"
        )

        if option != "Choose option":
            st.markdown("### 📁 Upload Audio File")
            audio_file = st.file_uploader(
                "",
                type=["mp3", "wav", "ogg", "flac"],
                help="Upload your audio file (max 200MB)"
            )
            
            if audio_file is not None:
                # Audio preview
                st.markdown("### 🎧 Audio Preview")
                st.audio(audio_file, format="audio/*")
                
                # File info
                file_size = len(audio_file.read()) / (1024 * 1024)  # MB
                audio_file.seek(0)  # Reset file pointer
                st.info(f"📊 File: {audio_file.name} | Size: {file_size:.1f} MB")
                
                # Process button with custom styling
                st.markdown("### 🚀 Start Processing")
                
                if st.button("🎵 Transcribe Audio", type="primary", use_container_width=True):
                    # Save the uploaded audio file
                    temp_audio_path = "temp_audio." + audio_file.name.split(".")[-1]
                    with open(temp_audio_path, "wb") as f:
                        f.write(audio_file.read())

                    # Processing started message
                    st.markdown("""
                    <div style="background: linear-gradient(90deg, #ffeaa7 0%, #fab1a0 100%); 
                                padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                        <h4 style="margin: 0; text-align: center;">
                            🔄 Processing started... Please wait for the transcription to complete. 
                            This may take some time
                        </h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Process with initial transcription
                    def process_transcription(use_gemini=False):
                        if option == "Hindi":
                            output = run_backend_script("hindi1.py", temp_audio_path, use_gemini)
                            filename = "hindi_lyrics"
                            language_flag = "🇮🇳"
                        elif option == "English":
                            output = run_backend_script("main.py", temp_audio_path, use_gemini)
                            filename = "english_lyrics"
                            language_flag = "🇺🇸"
                        elif option == "Bilingual":
                            output = run_backend_script("bilingual.py", temp_audio_path, use_gemini)
                            filename = "bilingual_lyrics"
                            language_flag = "🌏"
                        return output, filename, language_flag

                    # Initial transcription
                    output, filename, language_flag = process_transcription()

                    # Clean up temporary file
                    try:
                        os.remove(temp_audio_path)
                    except:
                        pass

                    # Results section
                    if output:
                        st.markdown("---")
                        st.markdown(f"### {language_flag} Transcription Results")
                        
                        # Extract clean lyrics for display
                        lines = output.split('\n')
                        clean_lyrics = []
                        for line in lines:
                            if not any(marker in line for marker in ['[INFO]', '[SUCCESS]', '[ERROR]', 'INFO:spleeter']):
                                clean_line = line.strip()
                                if clean_line and not clean_line.startswith('='):
                                    clean_lyrics.append(clean_line)
                        
                        final_lyrics = '\n'.join(clean_lyrics)
                        
                        if final_lyrics:
                            # Display lyrics in a nice container
                            st.markdown("""
                            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; 
                                        border-left: 4px solid #667eea; margin: 1rem 0;">
                            """, unsafe_allow_html=True)
                            
                            st.text_area(
                                "📝 Your Lyrics:",
                                value=final_lyrics,
                                height=300,
                                help="Your transcribed lyrics are ready!"
                            )
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Feedback section
                            st.markdown("### 🤔 How's the Quality?")
                            col_feedback1, col_feedback2 = st.columns(2)
                            
                            with col_feedback1:
                                if st.button("👍 Good Quality"):
                                    st.success("Thanks for the feedback! 🌟")
                            
                            with col_feedback2:
                                if st.button("👎 Try Improving"):
                                    st.info("🔄 Retrying with enhanced AI model...")
                                    output, filename, language_flag = process_transcription(use_gemini=True)
                                    
                                    # Display improved results
                                    if output:
                                        st.markdown("### ✨ Enhanced Translation")
                                        lines = output.split('\n')
                                        clean_lyrics = []
                                        for line in lines:
                                            if not any(marker in line for marker in ['[INFO]', '[SUCCESS]', '[ERROR]', 'INFO:spleeter']):
                                                clean_line = line.strip()
                                                if clean_line and not clean_line.startswith('='):
                                                    clean_lyrics.append(clean_line)
                                        
                                        improved_lyrics = '\n'.join(clean_lyrics)
                                        if improved_lyrics:
                                            st.text_area(
                                                "📝 Improved Lyrics:",
                                                value=improved_lyrics,
                                                height=300,
                                                help="Enhanced translation using Gemini AI"
                                            )
                            
                            # Download section
                            st.markdown("### 📥 Download Options")
                            col_download1, col_download2 = st.columns(2)
                            
                            with col_download1:
                                create_download_button(output, filename)
                            
                            with col_download2:
                                st.success("✅ Processing completed successfully!")
                                
                        else:
                            st.warning("⚠️ No lyrics content found in the output. Please try again.")
                    else:
                        st.error("❌ Transcription failed. Please check your audio file and try again.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Made with ❤️ using Streamlit • Powered by AI Transcription Technology</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()