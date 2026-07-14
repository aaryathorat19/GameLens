"""Audio-energy based candidate detection for football highlights."""

from dataclasses import dataclass
from pathlib import Path
import wave

import numpy as np


class AudioAnalysisError(RuntimeError):
    """Raised when a WAV audio track cannot be analyzed."""


@dataclass(frozen=True)
class HighlightCandidate:
    """A time range whose crowd/commentary audio is unusually energetic."""

    start_seconds: float
    end_seconds: float
    score: float

    @property
    def duration_seconds(self) -> float:
        return self.end_seconds - self.start_seconds


def _load_pcm_wav(audio_path: Path) -> tuple[np.ndarray, int]:
    if not audio_path.is_file() or audio_path.suffix.lower() != ".wav":
        raise AudioAnalysisError("Select a valid extracted WAV audio file.")
    try:
        with wave.open(str(audio_path), "rb") as wav_file:
            if wav_file.getcomptype() != "NONE" or wav_file.getsampwidth() != 2:
                raise AudioAnalysisError("Audio analysis requires an uncompressed 16-bit WAV file.")
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            samples = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype="<i2")
    except wave.Error as error:
        raise AudioAnalysisError("The extracted audio file is not a readable WAV file.") from error

    if sample_rate <= 0 or samples.size == 0:
        raise AudioAnalysisError("The extracted audio file has no samples.")
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    return samples.astype(np.float32) / np.iinfo(np.int16).max, sample_rate


def _energy_windows(samples: np.ndarray, sample_rate: int, frame_seconds: float, hop_seconds: float) -> tuple[np.ndarray, np.ndarray]:
    frame_size = max(1, round(sample_rate * frame_seconds))
    hop_size = max(1, round(sample_rate * hop_seconds))
    starts = np.arange(0, max(1, samples.size - frame_size + 1), hop_size)
    energies = np.array(
        [np.sqrt(np.mean(np.square(samples[start : start + frame_size]))) for start in starts]
    )
    return starts / sample_rate, energies


def detect_audio_candidates(
    audio_path: Path,
    *,
    frame_seconds: float = 1.0,
    hop_seconds: float = 0.5,
    energy_percentile: float = 90.0,
    min_duration_seconds: float = 2.0,
    merge_gap_seconds: float = 3.0,
) -> list[HighlightCandidate]:
    """Find contiguous high-energy windows and return ranked candidate moments."""
    if frame_seconds <= 0 or hop_seconds <= 0:
        raise ValueError("Frame and hop durations must be positive.")
    if not 0 < energy_percentile < 100:
        raise ValueError("Energy percentile must be between 0 and 100.")

    samples, sample_rate = _load_pcm_wav(audio_path)
    starts, energies = _energy_windows(samples, sample_rate, frame_seconds, hop_seconds)
    threshold = np.percentile(energies, energy_percentile)
    active = np.flatnonzero(energies >= threshold)
    if active.size == 0 or np.allclose(energies, 0):
        return []

    candidates: list[HighlightCandidate] = []
    group_start = active[0]
    group_end = active[0]
    for index in active[1:]:
        gap = starts[index] - (starts[group_end] + frame_seconds)
        if gap <= merge_gap_seconds:
            group_end = index
            continue
        candidates.extend(_build_candidate(starts, energies, group_start, group_end, frame_seconds, min_duration_seconds))
        group_start = group_end = index
    candidates.extend(_build_candidate(starts, energies, group_start, group_end, frame_seconds, min_duration_seconds))
    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)


def _build_candidate(
    starts: np.ndarray,
    energies: np.ndarray,
    first: int,
    last: int,
    frame_seconds: float,
    min_duration_seconds: float,
) -> list[HighlightCandidate]:
    start = float(starts[first])
    end = float(starts[last] + frame_seconds)
    if end - start < min_duration_seconds:
        return []
    peak = float(np.max(energies))
    score = 0.0 if peak == 0 else float(np.max(energies[first : last + 1]) / peak)
    return [HighlightCandidate(start, end, score)]
