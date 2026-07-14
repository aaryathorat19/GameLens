# GameLens

An AI-powered football highlight generator and match analyzer. Upload a full match recording and turn it into a longer, customizable highlight experience.

## Current status

Highlights pipeline and match statistics dashboard are in place. Next milestone: AI match summaries.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

FFmpeg must also be installed and available on your `PATH` before video-processing milestones can run.

Optional live statistics: copy `.env.example` to `.env` and set `API_FOOTBALL_KEY` to your [API-Football](https://dashboard.api-football.com/) key. Without it, the dashboard serves a built-in demo fixture.

## Commit roadmap

1. **chore: bootstrap GameLens application** - structure, configuration, dependencies, and Streamlit shell.
2. **feat: add video upload and audio extraction** - validate MP4 uploads, persist the source video, extract WAV with FFmpeg.
3. **feat: detect audio highlight candidates** - loudness/energy analysis, candidate timestamps, and tests.
4. **feat: refine candidates with scene detection** - PySceneDetect boundaries and clip windows.
5. **feat: generate downloadable highlight video** - extract clips, merge `Highlights.mp4`, processing progress/errors.
6. **feat: add highlight controls and preview** - Short/Medium/Extended profiles, event filters, confidence scores, player and download.
7. **feat: add match statistics dashboard** - provider abstraction, API integration, statistics cards, and event timeline.
8. **feat: generate AI match summaries** - summary service, graceful configuration and failure states.
9. **feat: add scoreboard OCR and replay detection** - optional advanced-analysis pipeline.
10. **feat: add player and ball tracking analytics** - YOLO pipeline, tracking, formations, heatmaps, and pass networks.

Each item is deliberately small enough to review and commit independently.
