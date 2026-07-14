# Current State

## System

```text
Streamlit browser UI -> upload -> WAV -> audio candidates -> scene-aligned windows
                            -> modules.highlight_selection.select_candidates()
                            -> services.highlight_renderer.render_highlights()
                            -> output/Highlights.mp4 -> player/download
```

`app.py` renders the pipeline and keeps paths/results in Streamlit session state. `modules/audio_highlights.py` computes RMS-energy candidates; `modules/scene_refinement.py` aligns and merges them with PySceneDetect scenes. `modules/highlight_selection.py` applies Short/Medium/Extended duration budgets and a confidence threshold before rendering, reducing FFmpeg work. `services/highlight_renderer.py` re-encodes selected windows, concatenates normalized clips, and writes `output/Highlights.mp4`. No environment variables, network calls, database, users, routes, or background workers exist.

## Directory map

| Path | Responsibility |
| --- | --- |
| `app.py` | Streamlit entry point and UI composition. |
| `config.py` | Project paths, UI identity, runtime-directory creation. |
| `modules/video_upload.py` | MP4 validation and safe server-side upload storage. |
| `modules/audio_highlights.py` | RMS audio-energy candidate detection and scores. |
| `modules/scene_refinement.py` | PySceneDetect scene windows and candidate alignment. |
| `modules/highlight_selection.py` | Confidence and duration-budget clip selection. |
| `services/audio_extractor.py` | FFmpeg preflight and WAV extraction. |
| `services/highlight_renderer.py` | FFmpeg clip extraction and `Highlights.mp4` rendering. |
| `utils/` | Reserved for shared helpers. |
| `input/` | User source videos at runtime; ignored by Git. |
| `output/` | Generated artifacts at runtime; ignored by Git. |
| `assets/` | Static project assets. |
| `tests/` | Automated tests; currently tests runtime-directory setup. |

## Dependencies

| Package | Intended role | Status |
| --- | --- | --- |
| Streamlit | Dashboard/UI | Used. |
| FFmpeg | Audio extraction now; clip extraction/merging later. |
| librosa, NumPy, SciPy | Audio candidate detection | Planned. |
| OpenCV, PySceneDetect | Scene analysis/refinement | Planned. |
| pytest | Tests | Declared; not yet installed in the local environment. |

## Data and request flow

No request/API/database flow exists. Current pipeline: MP4 upload -> persisted input -> WAV -> audio candidates -> scene windows -> budgeted clips -> `Highlights.mp4` -> player/download. Intended continuation: match statistics.

## Security and performance

No auth or secrets currently exist. Future upload handling must validate extensions, file size, duration, and paths; process only server-owned paths; clean temporary files; avoid loading whole match videos into memory. API tokens must be environment variables and excluded through `.env`.
