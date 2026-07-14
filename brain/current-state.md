# Current State

## System

```text
Streamlit browser UI -> app.main() -> modules.video_upload.save_uploaded_video()
                                     -> input/match_<uuid>.mp4
                                     -> services.audio_extractor.extract_audio()
                                     -> output/match_<uuid>_audio.wav
```

`app.py` renders the upload workflow and keeps source paths in Streamlit session state. `modules/video_upload.py` validates MP4 uploads and assigns generated names. `services/audio_extractor.py` calls FFmpeg to make mono 16 kHz WAV audio. `config.py` derives all paths from its own file location; no environment variables, network calls, database, users, routes, or background workers exist.

## Directory map

| Path | Responsibility |
| --- | --- |
| `app.py` | Streamlit entry point and UI composition. |
| `config.py` | Project paths, UI identity, runtime-directory creation. |
| `modules/video_upload.py` | MP4 validation and safe server-side upload storage. |
| `services/audio_extractor.py` | FFmpeg preflight and WAV extraction. |
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

No request/API/database flow exists. Current pipeline: MP4 upload -> persisted input -> extracted WAV. Intended continuation: candidates -> scene refinement -> clips -> `Highlights.mp4` -> dashboard/download.

## Security and performance

No auth or secrets currently exist. Future upload handling must validate extensions, file size, duration, and paths; process only server-owned paths; clean temporary files; avoid loading whole match videos into memory. API tokens must be environment variables and excluded through `.env`.
