from pathlib import Path
from subprocess import CompletedProcess

from modules.audio_highlights import HighlightCandidate
from services import highlight_renderer


def test_render_highlights_extracts_and_concatenates_clips(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "match.mp4"
    source.write_bytes(b"video")
    output = tmp_path / "Highlights.mp4"
    calls: list[list[str]] = []

    monkeypatch.setattr(highlight_renderer, "ffmpeg_available", lambda: True)

    def fake_run(command, **_kwargs):
        calls.append(command)
        target = Path(command[-1])
        if target.suffix == ".mp4":
            target.write_bytes(b"video")
        return CompletedProcess(command, 0)

    monkeypatch.setattr(highlight_renderer, "run", fake_run)

    result = highlight_renderer.render_highlights(
        source,
        [HighlightCandidate(1.0, 3.0, 0.8), HighlightCandidate(5.0, 8.0, 0.7)],
        output_path=output,
    )

    assert result == output
    assert output.is_file()
    assert len(calls) == 3
    assert "concat" in calls[-1]
