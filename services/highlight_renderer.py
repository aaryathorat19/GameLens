"""FFmpeg clip extraction and highlight-video rendering."""

from collections.abc import Callable
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory

from config import OUTPUT_DIR
from modules.audio_highlights import HighlightCandidate
from services.audio_extractor import ffmpeg_available


class HighlightRenderError(RuntimeError):
    """Raised when FFmpeg cannot render the highlight video."""


def render_highlights(
    source_video: Path,
    candidates: list[HighlightCandidate],
    *,
    output_path: Path = OUTPUT_DIR / "Highlights.mp4",
    progress_callback: Callable[[int, int], None] | None = None,
) -> Path:
    """Re-encode selected windows and concatenate them into one MP4 file."""
    if not source_video.is_file() or source_video.suffix.lower() != ".mp4":
        raise HighlightRenderError("Select a valid saved MP4 match recording.")
    if not candidates:
        raise HighlightRenderError("No scene-refined candidates are available to render.")
    if not ffmpeg_available():
        raise HighlightRenderError("FFmpeg is not installed or is not available on PATH.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="gamelens_", dir=output_path.parent) as temporary_dir:
        temporary = Path(temporary_dir)
        clips = []
        for index, candidate in enumerate(candidates, start=1):
            clip_path = temporary / f"clip_{index:03d}.mp4"
            _extract_clip(source_video, candidate, clip_path)
            clips.append(clip_path)
            if progress_callback:
                progress_callback(index, len(candidates))

        concat_file = temporary / "clips.txt"
        concat_file.write_text(
            "".join(f"file '{clip.as_posix()}'\n" for clip in clips), encoding="utf-8"
        )
        _run_ffmpeg(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(output_path),
            ]
        )

    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise HighlightRenderError("FFmpeg finished without creating Highlights.mp4.")
    return output_path


def _extract_clip(source_video: Path, candidate: HighlightCandidate, clip_path: Path) -> None:
    duration = candidate.duration_seconds
    if duration <= 0:
        raise HighlightRenderError("A candidate clip has an invalid duration.")
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{candidate.start_seconds:.3f}",
            "-i",
            str(source_video),
            "-t",
            f"{duration:.3f}",
            "-map",
            "0:v:0",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(clip_path),
        ]
    )


def _run_ffmpeg(command: list[str]) -> None:
    try:
        run(command, check=True, capture_output=True, text=True)
    except CalledProcessError as error:
        detail = error.stderr.strip() or "FFmpeg could not process the selected video clip."
        raise HighlightRenderError(detail) from error
