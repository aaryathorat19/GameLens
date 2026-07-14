from pathlib import Path
import wave

import numpy as np

from modules.audio_highlights import detect_audio_candidates


def _write_wav(path: Path, samples: np.ndarray, sample_rate: int = 100) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.astype("<i2").tobytes())


def test_detect_audio_candidates_finds_loud_segment(tmp_path: Path) -> None:
    quiet = np.zeros(200, dtype=np.int16)
    loud = np.full(300, 20_000, dtype=np.int16)
    audio_path = tmp_path / "match.wav"
    _write_wav(audio_path, np.concatenate([quiet, loud, quiet]))

    candidates = detect_audio_candidates(
        audio_path,
        frame_seconds=1.0,
        hop_seconds=1.0,
        energy_percentile=80.0,
        min_duration_seconds=2.0,
    )

    assert len(candidates) == 1
    assert candidates[0].start_seconds == 2.0
    assert candidates[0].end_seconds >= 5.0
    assert candidates[0].score == 1.0


def test_detect_audio_candidates_ignores_silence(tmp_path: Path) -> None:
    audio_path = tmp_path / "silent.wav"
    _write_wav(audio_path, np.zeros(500, dtype=np.int16))

    assert detect_audio_candidates(audio_path) == []
