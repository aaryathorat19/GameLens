# Current State

## System

```text
Streamlit browser UI -> app.main() -> config.ensure_directories()
                                     -> input/, output/, assets/
```

`app.py` renders a static product shell and planned workflow. `config.py` derives all paths from its own file location; no environment variables, network calls, persistence, users, routes, or background workers exist.

## Directory map

| Path | Responsibility |
| --- | --- |
| `app.py` | Streamlit entry point and UI composition. |
| `config.py` | Project paths, UI identity, runtime-directory creation. |
| `modules/` | Reserved for analysis/generation domain modules. |
| `services/` | Reserved for external integrations, e.g. football APIs. |
| `utils/` | Reserved for shared helpers. |
| `input/` | User source videos at runtime; ignored by Git. |
| `output/` | Generated artifacts at runtime; ignored by Git. |
| `assets/` | Static project assets. |
| `tests/` | Automated tests; currently tests runtime-directory setup. |

## Dependencies

| Package | Intended role | Status |
| --- | --- | --- |
| Streamlit | Dashboard/UI | Used. |
| MoviePy, FFmpeg | Clip extraction/merging | Planned. |
| librosa, NumPy, SciPy | Audio candidate detection | Planned. |
| OpenCV, PySceneDetect | Scene analysis/refinement | Planned. |
| pytest | Tests | Declared; not yet installed in the local environment. |

## Data and request flow

No request/API/database flow exists. Intended pipeline: MP4 upload -> persisted input -> extracted audio -> candidate moments -> scene refinement -> clips -> `Highlights.mp4` -> dashboard/download.

## Security and performance

No auth or secrets currently exist. Future upload handling must validate extensions, file size, duration, and paths; process only server-owned paths; clean temporary files; avoid loading whole match videos into memory. API tokens must be environment variables and excluded through `.env`.
