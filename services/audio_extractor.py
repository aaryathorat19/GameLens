"""FFmpeg-backed audio extraction for uploaded match recordings."""

from pathlib import Path
from shutil import which
from subprocess import CalledProcessError, run

from config import OUTPUT_DIR


class AudioExtractionError(RuntimeError):
    """Raised when FFmpeg cannot produce a usable WAV audio track."""


def ffmpeg_available() -> bool:
    """Return whether FFmpeg can be called from the current environment."""
    return which("ffmpeg") is not None


def extract_audio(video_path: Path, output_dir: Path = OUTPUT_DIR) -> Path:
    """Extract mono 16 kHz PCM WAV audio from an MP4 recording."""
    if video_path.suffix.lower() != ".mp4" or not video_path.is_file():
        raise AudioExtractionError("The saved match recording is not a valid MP4 file.")
    if not ffmpeg_available():
        raise AudioExtractionError(
            "FFmpeg is not installed or is not available on PATH. Install FFmpeg and retry."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{video_path.stem}_audio.wav"
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(audio_path),
    ]
    try:
        run(command, check=True, capture_output=True, text=True)
    except CalledProcessError as error:
        detail = error.stderr.strip() or "FFmpeg could not read the uploaded video."
        raise AudioExtractionError(detail) from error

    if not audio_path.is_file():
        raise AudioExtractionError("FFmpeg finished without creating an audio file.")
    return audio_path
