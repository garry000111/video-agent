
import os
from pathlib import Path

import yt_dlp
from pydub import AudioSegment

# FFmpeg installation
FFMPEG_DIR = (
    Path(os.environ["LOCALAPPDATA"])
    / "Microsoft"
    / "WinGet"
    / "Packages"
    / "Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe"
    / "ffmpeg-9.0.2-full_build-shared"
    / "bin"
)

FFMPEG_EXE = FFMPEG_DIR / "ffmpeg.exe"
FFPROBE_EXE = FFMPEG_DIR / "ffprobe.exe"

if not FFMPEG_EXE.is_file() or not FFPROBE_EXE.is_file():
    raise FileNotFoundError(f"FFmpeg or FFprobe not found in {FFMPEG_DIR}")

# Make FFmpeg visible to pydub and subprocesses
os.environ["PATH"] = str(FFMPEG_DIR) + os.pathsep + os.environ["PATH"]
AudioSegment.converter = str(FFMPEG_EXE)
AudioSegment.ffprobe = str(FFPROBE_EXE)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
        "ffmpeg_location": str(FFMPEG_DIR),
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        wav_path = str(Path(filename).with_suffix(".wav"))

    if not os.path.isfile(wav_path):
        raise FileNotFoundError(f"Expected WAV file was not created: {wav_path}")

    return wav_path


def convert_to_wav(input_path: str) -> str:
    """Convert a local audio/video file to mono, 16 kHz WAV."""
    output_path = str(Path(input_path).with_name(
        Path(input_path).stem + "_converted.wav"
    ))

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    if chunk_minutes <= 0:
        raise ValueError("chunk_minutes must be positive")

    audio = AudioSegment.from_wav(wav_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]
        chunk_path = f"{Path(wav_path).with_suffix('')}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list[str]:
    if source.startswith(("http://", "https://")):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
