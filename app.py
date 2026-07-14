"""Streamlit entry point for GameLens."""

from pathlib import Path

import streamlit as st

from config import APP_TAGLINE, APP_TITLE, ensure_directories
from modules.audio_highlights import AudioAnalysisError, detect_audio_candidates
from modules.scene_refinement import (
    SceneDetectionError,
    detect_scene_windows,
    refine_candidates_with_scenes,
)
from modules.video_upload import UploadValidationError, save_uploaded_video
from services.audio_extractor import AudioExtractionError, extract_audio, ffmpeg_available
from services.highlight_renderer import HighlightRenderError, render_highlights


def main() -> None:
    ensure_directories()
    st.set_page_config(page_title=APP_TITLE, page_icon="football", layout="wide")

    st.title(APP_TITLE)
    st.caption(APP_TAGLINE)
    st.info("Phase 5: generate a downloadable highlight video from refined match moments.")

    uploaded_video = st.file_uploader("Upload a match recording (MP4)", type=["mp4"])
    if uploaded_video is None:
        st.caption("Maximum upload size: 500 MB. The original video stays local to this project.")
    else:
        st.video(uploaded_video)
        if st.button("Prepare audio", type="primary"):
            if not ffmpeg_available():
                st.error("FFmpeg is required. Install it, add it to PATH, then restart Streamlit.")
                return
            try:
                with st.spinner("Saving the match recording and extracting audio..."):
                    saved_video = save_uploaded_video(uploaded_video)
                    audio_path = extract_audio(saved_video)
                st.session_state["source_video"] = str(saved_video)
                st.session_state["source_audio"] = str(audio_path)
                st.success("Audio track is ready for highlight analysis.")
            except (UploadValidationError, AudioExtractionError) as error:
                st.error(str(error))

    source_audio = st.session_state.get("source_audio")
    if source_audio and Path(source_audio).is_file():
        st.subheader("Extracted match audio")
        st.audio(source_audio)
        if st.button("Detect highlight candidates"):
            try:
                with st.spinner("Analyzing crowd and commentary energy..."):
                    candidates = detect_audio_candidates(Path(source_audio))
                st.session_state["highlight_candidates"] = candidates
            except AudioAnalysisError as error:
                st.error(str(error))

    candidates = st.session_state.get("highlight_candidates", [])
    if candidates:
        st.subheader("Candidate highlight moments")
        st.caption("Higher score means louder audio relative to this match.")
        st.dataframe(
            [
                {
                    "Start (s)": round(candidate.start_seconds, 1),
                    "End (s)": round(candidate.end_seconds, 1),
                    "Duration (s)": round(candidate.duration_seconds, 1),
                    "Audio score": round(candidate.score, 2),
                }
                for candidate in candidates
            ],
            use_container_width=True,
            hide_index=True,
        )

    source_video = st.session_state.get("source_video")
    if candidates and source_video and Path(source_video).is_file():
        if st.button("Refine candidates with scene detection"):
            try:
                with st.spinner("Detecting video scene boundaries..."):
                    scenes = detect_scene_windows(Path(source_video))
                    refined = refine_candidates_with_scenes(candidates, scenes)
                st.session_state["refined_candidates"] = refined
                st.success(f"Aligned {len(refined)} candidate clips using {len(scenes)} detected scenes.")
            except SceneDetectionError as error:
                st.error(str(error))

    refined_candidates = st.session_state.get("refined_candidates", [])
    if refined_candidates:
        st.subheader("Scene-refined clip windows")
        st.dataframe(
            [
                {
                    "Start (s)": round(candidate.start_seconds, 1),
                    "End (s)": round(candidate.end_seconds, 1),
                    "Duration (s)": round(candidate.duration_seconds, 1),
                    "Audio score": round(candidate.score, 2),
                }
                for candidate in refined_candidates
            ],
            use_container_width=True,
            hide_index=True,
        )
        if source_video and Path(source_video).is_file():
            if st.button("Generate Highlights.mp4", type="primary"):
                progress = st.progress(0, text="Preparing highlight clips...")

                def update_progress(completed: int, total: int) -> None:
                    progress.progress(completed / total, text=f"Rendering clip {completed} of {total}...")

                try:
                    output_path = render_highlights(
                        Path(source_video), refined_candidates, progress_callback=update_progress
                    )
                    st.session_state["highlight_video"] = str(output_path)
                    progress.progress(1.0, text="Highlights.mp4 is ready.")
                except HighlightRenderError as error:
                    progress.empty()
                    st.error(str(error))

    highlight_video = st.session_state.get("highlight_video")
    if highlight_video and Path(highlight_video).is_file():
        st.subheader("Generated highlights")
        st.video(highlight_video)
        with Path(highlight_video).open("rb") as video_file:
            st.download_button(
                "Download Highlights.mp4",
                data=video_file.read(),
                file_name="Highlights.mp4",
                mime="video/mp4",
            )

    st.subheader("How it will work")
    st.markdown(
        "1. Upload a full match recording.\n"
        "2. Prepare its audio track, rank high-energy moments, and align them to scenes.\n"
        "3. Generate, preview, and download Highlights.mp4."
    )


if __name__ == "__main__":
    main()
