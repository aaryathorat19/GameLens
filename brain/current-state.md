# Current State

## System

```text
Streamlit browser UI -> upload -> WAV -> audio candidates -> scene-aligned windows
                            -> modules.highlight_selection.select_candidates()
                            -> services.highlight_renderer.render_highlights()
                            -> output/Highlights.mp4 -> player/download
Streamlit browser UI -> services.stats_provider.get_stats_provider()
                            -> DemoStatsProvider | ApiFootballStatsProvider
                            -> modules.match_stats.MatchStatistics
                            -> stats cards + event timeline
```

`app.py` renders the pipeline and keeps paths/results in Streamlit session state. `modules/audio_highlights.py` computes RMS-energy candidates; `modules/scene_refinement.py` aligns and merges them with PySceneDetect scenes. `modules/highlight_selection.py` applies Short/Medium/Extended duration budgets and a confidence threshold before rendering, reducing FFmpeg work. `services/highlight_renderer.py` re-encodes selected windows, concatenates normalized clips, and writes `output/Highlights.mp4`. Match statistics come from `services/stats_provider.py` (offline demo or API-Football when `API_FOOTBALL_KEY` is set). No database, users, routes, or background workers exist.

## Directory map

| Path | Responsibility |
| --- | --- |
| `app.py` | Streamlit entry point and UI composition. |
| `config.py` | Project paths, UI identity, API defaults, runtime-directory creation. |
| `modules/video_upload.py` | MP4 validation and safe server-side upload storage. |
| `modules/audio_highlights.py` | RMS audio-energy candidate detection and scores. |
| `modules/scene_refinement.py` | PySceneDetect scene windows and candidate alignment. |
| `modules/highlight_selection.py` | Confidence and duration-budget clip selection. |
| `modules/match_stats.py` | Normalized match statistics/event models and formatting helpers. |
| `services/audio_extractor.py` | FFmpeg preflight and WAV extraction. |
| `services/highlight_renderer.py` | FFmpeg clip extraction and `Highlights.mp4` rendering. |
| `services/stats_provider.py` | Stats provider interface, demo backend, API-Football client. |
| `utils/` | Reserved for shared helpers. |
| `input/` | User source videos at runtime; ignored by Git. |
| `output/` | Generated artifacts at runtime; ignored by Git. |
| `assets/` | Static project assets. |
| `tests/` | Automated tests for deterministic modules/providers. |

## Dependencies

| Package | Intended role | Status |
| --- | --- | --- |
| Streamlit | Dashboard/UI | Used. |
| FFmpeg | Audio extraction and highlight clip merge. | Used. |
| librosa, NumPy, SciPy | Audio candidate detection | Used. |
| OpenCV, PySceneDetect | Scene analysis/refinement | Used. |
| pytest | Tests | Used. |
| API-Football | Live match statistics | Optional; `API_FOOTBALL_KEY` in `.env`. |

## Data and request flow

Highlight pipeline: MP4 upload -> persisted input -> WAV -> audio candidates -> scene windows -> budgeted clips -> `Highlights.mp4` -> player/download. Statistics path: demo or API-Football fixture/statistics/events -> `MatchStatistics` -> Streamlit cards/timeline. Intended continuation: AI match summaries.

## Security and performance

No auth exists. Live statistics require `API_FOOTBALL_KEY` from the environment (`.env` is gitignored). HTTP calls use a fixed timeout and map provider errors into user-readable messages. Upload handling validates extensions and processes only server-owned paths.
