from modules.audio_highlights import HighlightCandidate
from modules.highlight_selection import PROFILES, select_candidates, total_duration


def test_select_candidates_uses_highest_scores_within_budget() -> None:
    candidates = [
        HighlightCandidate(0.0, 100.0, 0.7),
        HighlightCandidate(120.0, 220.0, 0.9),
        HighlightCandidate(240.0, 340.0, 0.8),
    ]

    selected = select_candidates(candidates, PROFILES["Short"], 0.0)

    assert [(item.start_seconds, item.end_seconds) for item in selected] == [
        (120.0, 220.0),
        (240.0, 260.0),
    ]
    assert total_duration(selected) == 120.0


def test_select_candidates_applies_confidence_threshold() -> None:
    candidates = [HighlightCandidate(0.0, 20.0, 0.4), HighlightCandidate(30.0, 50.0, 0.8)]

    selected = select_candidates(candidates, PROFILES["Short"], 0.5)

    assert selected == [HighlightCandidate(30.0, 50.0, 0.8)]
