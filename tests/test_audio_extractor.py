from pathlib import Path
from subprocess import CompletedProcess

import pytest

from services import audio_extractor


def test_extract_audio_invokes_ffmpeg_with_audio_only_options(tmp_path: Path, monkeypatch) -> None:
    video = tmp_path / "match.mp4"
    video.write_bytes(b"video")
    output = tmp_path / "output"
    captured: list[str] = []

    monkeypatch.setattr(audio_extractor, "ffmpeg_available", lambda: True)

    def fake_run(command, **_kwargs):
        captured.extend(command)
        Path(command[-1]).write_bytes(b"wav")
        return CompletedProcess(command, 0)

    monkeypatch.setattr(audio_extractor, "run", fake_run)

    audio = audio_extractor.extract_audio(video, output)

    assert audio.is_file()
    assert "-vn" in captured
    assert captured[captured.index("-ar") + 1] == "16000"


def test_extract_audio_requires_ffmpeg(tmp_path: Path, monkeypatch) -> None:
    video = tmp_path / "match.mp4"
    video.write_bytes(b"video")
    monkeypatch.setattr(audio_extractor, "ffmpeg_available", lambda: False)

    with pytest.raises(audio_extractor.AudioExtractionError, match="FFmpeg"):
        audio_extractor.extract_audio(video)
