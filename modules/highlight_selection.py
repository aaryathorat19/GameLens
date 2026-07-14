"""Budget-aware selection controls for efficient highlight rendering."""

from dataclasses import dataclass

from modules.audio_highlights import HighlightCandidate


@dataclass(frozen=True)
class HighlightProfile:
    """A user-facing total-duration budget for a generated highlights video."""

    name: str
    max_duration_seconds: float


PROFILES = {
    "Short": HighlightProfile("Short", 120.0),
    "Medium": HighlightProfile("Medium", 300.0),
    "Extended": HighlightProfile("Extended", 600.0),
}


def select_candidates(
    candidates: list[HighlightCandidate],
    profile: HighlightProfile,
    minimum_confidence: float,
    *,
    minimum_clip_seconds: float = 5.0,
) -> list[HighlightCandidate]:
    """Choose the highest-confidence moments within the profile's time budget.

    Selecting before FFmpeg work prevents rendering clips that cannot appear in
    the final video. The returned list is chronological for natural playback.
    """
    if not 0.0 <= minimum_confidence <= 1.0:
        raise ValueError("Minimum confidence must be between 0 and 1.")

    remaining = profile.max_duration_seconds
    selected: list[HighlightCandidate] = []
    for candidate in sorted(candidates, key=lambda item: item.score, reverse=True):
        if candidate.score < minimum_confidence or remaining < minimum_clip_seconds:
            continue
        duration = min(candidate.duration_seconds, remaining)
        if duration < minimum_clip_seconds:
            continue
        selected.append(
            HighlightCandidate(candidate.start_seconds, candidate.start_seconds + duration, candidate.score)
        )
        remaining -= duration
    return sorted(selected, key=lambda item: item.start_seconds)


def total_duration(candidates: list[HighlightCandidate]) -> float:
    """Return the combined duration for UI reporting."""
    return sum(candidate.duration_seconds for candidate in candidates)
