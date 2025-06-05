import streamlit as st
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="▶️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #FF4B4B;
    }
    .st-b7 {
        color: white;
    }
    .stDownloadButton button {
        background-color: #FF4B4B;
        color: white;
    }
    .stTextInput input {
        background-color: #0E1117;
        color: white;
    }
    .stRadio div[role="radiogroup"] > label {
        background-color: #0E1117;
        color: white;
        padding: 10px 15px;
        border-radius: 4px;
        margin-right: 10px;
    }
    .stRadio div[role="radiogroup"] > label:hover {
        background-color: #262730;
    }
    .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] {
        background-color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# Main function
def main():
    st.title("YouTube Downloader")
    st.markdown("Download videos, audio, or transcripts from YouTube")
    
    # Input form
    with st.form("download_form"):
        url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        mode = st.radio("Download Type", ("Video", "Audio", "Transcript"))
        
        submitted = st.form_submit_button("Download")
    
    if submitted and url:
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Map mode to command line argument
            mode_map = {
                "Video": "video",
                "Audio": "audio",
                "Transcript": "transcript"
            }
            
            # Call your existing script
            cmd = [
                "python", 
                "yt_downloader.py", 
                "-u", url, 
                "-m", mode_map[mode], 
                "-o", temp_dir
            ]
            
            status_text.text("Starting download...")
            progress_bar.progress(10)
            
            # Run subprocess with progress updates
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Display output in real-time
            output_container = st.empty()
            output_text = ""
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_text += output + "\n"
                    output_container.text(output_text)
                    progress_bar.progress(min(90, progress_bar.progress(0) + 5))
            
            # Check for errors
            if process.returncode != 0:
                error = process.stderr.read()
                raise Exception(error)
            
            # Find downloaded files
            files = []
            for root, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    files.append(Path(root) / filename)
            
            if not files:
                raise Exception("No files were downloaded")
            
            status_text.text("Processing complete!")
            progress_bar.progress(100)
            
            # Display download buttons
            st.success("Download completed successfully!")
            
            for file in files:
                with open(file, "rb") as f:
                    st.download_button(
                        label=f"Download {file.name}",
                        data=f,
                        file_name=file.name,
                        mime="application/octet-stream"
                    )
            
            # Clean up temp directory after download
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            st.error(f"Download failed: {str(e)}")
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
