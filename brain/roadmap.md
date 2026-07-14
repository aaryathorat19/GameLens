# Commit Roadmap

Each row is one reviewable commit. Do not combine milestones without an explicit reason.

| # | Commit | Deliverable |
| --- | --- | --- |
| 1 | `chore: bootstrap MatchVision application` | Structure, config, dependencies, Streamlit shell. Done. |
| 2 | `feat: add video upload and audio extraction` | MP4 validation/storage and FFmpeg WAV extraction. |
| 3 | `feat: detect audio highlight candidates` | Energy/loudness analysis and tested timestamp candidates. |
| 4 | `feat: refine candidates with scene detection` | PySceneDetect boundaries and clip-window selection. |
| 5 | `feat: generate downloadable highlight video` | Clip extraction, merge, progress/error UI, output artifact. |
| 6 | `feat: add highlight controls and preview` | Length profiles, filters, confidence, player/download. |
| 7 | `feat: add match statistics dashboard` | Provider interface, stats cards, event timeline. |
| 8 | `feat: generate AI match summaries` | Summary service and safe failure/config states. |
| 9 | `feat: add scoreboard OCR and replay detection` | Optional advanced-analysis services. |
| 10 | `feat: add player and ball tracking analytics` | YOLO/tracking/formation/heatmap/pass-network capabilities. |

## Phase-2 contract

Input: one MP4 from Streamlit uploader. Output: a server-managed source file and extracted WAV. No highlight scoring, scene analysis, or video merging in this commit. Require FFmpeg preflight and clear actionable errors.
