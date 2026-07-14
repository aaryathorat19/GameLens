"""Scene-boundary detection and candidate-window refinement."""

from dataclasses import dataclass
from pathlib import Path

from modules.audio_highlights import HighlightCandidate


class SceneDetectionError(RuntimeError):
    """Raised when PySceneDetect cannot analyze a source video."""


@dataclass(frozen=True)
class SceneWindow:
    """A contiguous scene boundary expressed in video seconds."""

    start_seconds: float
    end_seconds: float


def detect_scene_windows(video_path: Path, threshold: float = 27.0) -> list[SceneWindow]:
    """Detect content changes in an MP4 and return scene-aligned time windows."""
    if not video_path.is_file() or video_path.suffix.lower() != ".mp4":
        raise SceneDetectionError("Select a valid saved MP4 match recording.")
    try:
        from scenedetect import ContentDetector, detect

        scenes = detect(str(video_path), ContentDetector(threshold=threshold))
    except ImportError as error:
        raise SceneDetectionError("PySceneDetect is not installed. Run pip install -r requirements.txt.") from error
    except Exception as error:
        raise SceneDetectionError(f"Scene detection failed: {error}") from error
    return [
        SceneWindow(start.get_seconds(), end.get_seconds())
        for start, end in scenes
        if end.get_seconds() > start.get_seconds()
    ]


def refine_candidates_with_scenes(
    candidates: list[HighlightCandidate], scenes: list[SceneWindow]
) -> list[HighlightCandidate]:
    """Expand each audio candidate to the full scenes it overlaps."""
    if not scenes:
        return candidates

    refined: list[HighlightCandidate] = []
    for candidate in candidates:
        overlaps = [
            scene
            for scene in scenes
            if scene.start_seconds < candidate.end_seconds and scene.end_seconds > candidate.start_seconds
        ]
        if not overlaps:
            refined.append(candidate)
            continue
        refined.append(
            HighlightCandidate(
                start_seconds=min(scene.start_seconds for scene in overlaps),
                end_seconds=max(scene.end_seconds for scene in overlaps),
                score=candidate.score,
            )
        )
    return _merge_overlapping_candidates(refined)


def _merge_overlapping_candidates(candidates: list[HighlightCandidate]) -> list[HighlightCandidate]:
    """Avoid duplicate clip work when scene expansion makes candidates overlap."""
    if not candidates:
        return []
    ordered = sorted(candidates, key=lambda candidate: candidate.start_seconds)
    merged = [ordered[0]]
    for candidate in ordered[1:]:
        previous = merged[-1]
        if candidate.start_seconds <= previous.end_seconds:
            merged[-1] = HighlightCandidate(
                previous.start_seconds,
                max(previous.end_seconds, candidate.end_seconds),
                max(previous.score, candidate.score),
            )
        else:
            merged.append(candidate)
    return merged
