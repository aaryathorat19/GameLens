from modules.audio_highlights import HighlightCandidate
from modules.scene_refinement import SceneWindow, refine_candidates_with_scenes


def test_refine_candidates_expands_to_overlapping_scenes() -> None:
    candidates = [HighlightCandidate(12.0, 18.0, 0.8)]
    scenes = [SceneWindow(0.0, 10.0), SceneWindow(10.0, 15.0), SceneWindow(15.0, 25.0)]

    refined = refine_candidates_with_scenes(candidates, scenes)

    assert refined == [HighlightCandidate(10.0, 25.0, 0.8)]


def test_refine_candidates_merges_overlapping_results() -> None:
    candidates = [HighlightCandidate(11.0, 12.0, 0.6), HighlightCandidate(14.0, 16.0, 0.9)]
    scenes = [SceneWindow(10.0, 15.0), SceneWindow(15.0, 20.0)]

    refined = refine_candidates_with_scenes(candidates, scenes)

    assert refined == [HighlightCandidate(10.0, 20.0, 0.9)]
