import sys
import argparse
import os
import glob
from yt_dlp import YoutubeDL
from pytube import YouTube
import whisper


def ensure_dirs(base_output):
    video_dir = os.path.join(base_output, "video")
    audio_dir = os.path.join(base_output, "audio")
    transcript_dir = os.path.join(base_output, "transcripts")
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(transcript_dir, exist_ok=True)
    return video_dir, audio_dir, transcript_dir


def list_combined_formats(url: str):
    ydl_opts = {"quiet": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    formats = info.get("formats", [])
    return [
        f
        for f in formats
        if f.get("vcodec") not in (None, "none")
        and f.get("acodec") not in (None, "none")
    ]


def choose_format(formats: list):
    print("\nAvailable combined formats (video+audio):")
    print(f"{'idx':<4} {'format_id':<8} {'ext':<4} {'res':<8} {'fps':<5} {'note'}")
    print("-" * 60)
    for i, f in enumerate(formats):
        print(
            f"{i:<4} {f['format_id']:<8} {f['ext']:<4} "
            f"{f.get('resolution',''):<8} {str(f.get('fps','')):<5} "
            f"{f.get('format_note','')}"
        )
    while True:
        idx = input("Enter format index to download: ").strip()
        if idx.isdigit() and 0 <= int(idx) < len(formats):
            return formats[int(idx)]["format_id"]
        print("Invalid selection; try again.")


def download_video(url: str, out_dir: str):
    fmts = list_combined_formats(url)
    if fmts:
        fmt_id = choose_format(fmts)
    else:
        fmt_id = "bestvideo+bestaudio/best"
        print("No combined formats found; falling back to bestvideo+bestaudio.")
    ydl_opts = {
        "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
        "format": fmt_id,
        "merge_output_format": "mp4",
    }
    with YoutubeDL(ydl_opts) as ydl:
        print(f"\n⏳ Downloading video+audio as format {fmt_id}…")
        ydl.download([url])
    print("✅ Video download completed!")


def download_audio_and_get_path(url: str, out_dir: str):
    ydl_opts = {
        "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with YoutubeDL(ydl_opts) as ydl:
        print("⏳ Downloading and converting to MP3…")
        info = ydl.extract_info(url, download=True)
        filename = (
            ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        )
    print("✅ Audio downloaded.")
    return filename, info.get("title", "output")


def transcribe_audio(audio_path, title, out_dir):
    print("🔍 Transcribing with Whisper…")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    output_file = os.path.join(out_dir, f"{title}_transcript.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])
    print(f"✅ Transcript saved using Whisper to: {output_file}")


def clean_url(url: str) -> str:
    if "watch?v=" in url:
        return (
            url.split("&")[0].split("?")[0]
            + "?v="
            + url.split("watch?v=")[1].split("&")[0]
        )
    elif "youtu.be/" in url:
        return "https://www.youtube.com/watch?v=" + url.split("/")[-1].split("?")[0]
    return url


def download_transcript(url: str, out_dir: str, audio_dir: str):
    try:
        url = clean_url(url)
        print(f"[DEBUG] Initializing YouTube object with URL: {url}")
        yt = YouTube(url)

        print(f"[DEBUG] Video title: {yt.title}")
        print("[DEBUG] Available captions:")
        for lang in yt.captions:
            print(f" - {lang} (code: {yt.captions[lang].code})")

        caption = yt.captions.get_by_language_code("en")

        if caption:
            print("[DEBUG] Found English captions. Generating SRT...")
            transcript = caption.generate_srt_captions()
            filename = os.path.join(out_dir, f"{yt.title}_transcript.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"✅ Transcript saved to: {filename}")
        else:
            print("⚠️ No English captions found. Falling back to Whisper.")
            audio_path, title = download_audio_and_get_path(url, audio_dir)
            transcribe_audio(audio_path, title, out_dir)
    except Exception as e:
        print(f"❌ Captions failed, using Whisper instead. Reason: {e}")
        try:
            audio_path, title = download_audio_and_get_path(url, audio_dir)
            transcribe_audio(audio_path, title, out_dir)
        except Exception as e2:
            print(f"❌ Whisper transcription also failed: {e2}")


def main():
    parser = argparse.ArgumentParser(
        description="YouTube video/audio/transcript downloader with Whisper fallback"
    )
    parser.add_argument("-u", "--url", help="YouTube video URL")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["video", "audio", "transcript"],
        help="Download mode: 'video', 'audio' or 'transcript'",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="Base output folder (default: current directory)",
    )
    args = parser.parse_args()

    url = args.url or input("Paste YouTube URL: ").strip()
    mode = args.mode
    if not mode:
        while True:
            c = input("Download (v)ideo, (a)udio, or (t)ranscript? [v/a/t]: ").lower()
            if c in ("v", "video"):
                mode = "video"
                break
            if c in ("a", "audio"):
                mode = "audio"
                break
            if c in ("t", "transcript"):
                mode = "transcript"
                break
            print("Please enter 'v', 'a', or 't'.")

    video_dir, audio_dir, transcript_dir = ensure_dirs(args.output)
    print(f"\nURL    : {url}\nMode   : {mode}\n")

    try:
        if mode == "audio":
            download_audio_and_get_path(url, audio_dir)
        elif mode == "transcript":
            download_transcript(url, transcript_dir, audio_dir)
        else:
            download_video(url, video_dir)
    except Exception as e:
        print(f"❌ Download failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
