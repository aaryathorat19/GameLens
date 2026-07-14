"""Streamlit entry point for GameLens."""

from pathlib import Path
import os

import streamlit as st

from config import APP_TAGLINE, APP_TITLE, ensure_directories
from modules.audio_highlights import AudioAnalysisError, detect_audio_candidates
from modules.highlight_selection import PROFILES, select_candidates, total_duration
from modules.match_stats import format_optional, scoreline
from modules.scene_refinement import (
    SceneDetectionError,
    detect_scene_windows,
    refine_candidates_with_scenes,
)
from modules.video_upload import UploadValidationError, save_uploaded_video
from services.audio_extractor import AudioExtractionError, extract_audio, ffmpeg_available
from services.highlight_renderer import HighlightRenderError, render_highlights
from services.stats_provider import StatsProviderError, get_stats_provider


def main() -> None:
    ensure_directories()
    st.set_page_config(page_title=APP_TITLE, page_icon="football", layout="wide")

    st.title(APP_TITLE)
    st.caption(APP_TAGLINE)
    st.info("Phase 7: browse match statistics alongside generated highlights.")

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
        controls_left, controls_right = st.columns(2)
        with controls_left:
            profile_name = st.radio(
                "Highlight length", list(PROFILES), horizontal=True, index=1
            )
        with controls_right:
            minimum_confidence = st.slider(
                "Minimum audio confidence", min_value=0.0, max_value=1.0, value=0.5, step=0.05
            )

        selected_candidates = select_candidates(
            refined_candidates, PROFILES[profile_name], minimum_confidence
        )
        selected_duration = total_duration(selected_candidates)
        st.caption(
            f"{len(selected_candidates)} clips selected - {selected_duration:.0f}s of "
            f"{PROFILES[profile_name].max_duration_seconds:.0f}s available. "
            "Only selected clips are sent to FFmpeg."
        )
        if not selected_candidates:
            st.warning("No clips meet this confidence threshold. Lower it to generate highlights.")
        if source_video and Path(source_video).is_file():
            if st.button("Generate Highlights.mp4", type="primary", disabled=not selected_candidates):
                progress = st.progress(0, text="Preparing highlight clips...")

                def update_progress(completed: int, total: int) -> None:
                    progress.progress(completed / total, text=f"Rendering clip {completed} of {total}...")

                try:
                    output_path = render_highlights(
                        Path(source_video), selected_candidates, progress_callback=update_progress
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

    _render_match_statistics()

    st.subheader("How it will work")
    st.markdown(
        "1. Upload a full match recording.\n"
        "2. Rank and align high-energy moments, then apply a length/confidence budget.\n"
        "3. Render only the selected clips, then preview and download Highlights.mp4.\n"
        "4. Load match statistics for context while you review the highlights."
    )


def _render_match_statistics() -> None:
    st.subheader("Match statistics")
    api_configured = bool(os.getenv("API_FOOTBALL_KEY", "").strip())
    if api_configured:
        st.caption("Live API-Football access is configured via `.env`.")
    else:
        st.caption(
            "Use the demo fixture offline, or set API_FOOTBALL_KEY in `.env` for live fixture IDs."
        )
    source = st.radio(
        "Statistics source",
        ("Demo match", "Live API"),
        horizontal=True,
        index=1 if api_configured else 0,
    )
    match_id = st.text_input(
        "Fixture ID",
        value="demo" if source == "Demo match" else "",
        placeholder="API-Football numeric fixture ID",
        help="Demo accepts 'demo'. Live mode needs a numeric fixture ID from API-Football.",
    )
    if st.button("Load match statistics"):
        try:
            provider = get_stats_provider(prefer_live=source == "Live API")
            with st.spinner(f"Loading statistics from {provider.name}..."):
                stats = provider.get_match(match_id or "demo")
            st.session_state["match_statistics"] = stats
        except StatsProviderError as error:
            st.error(str(error))

    stats = st.session_state.get("match_statistics")
    if not stats:
        return

    st.markdown(
        f"**{stats.home.name}** {scoreline(stats)} **{stats.away.name}**  \n"
        f"{stats.competition} · {stats.status} · {stats.kickoff_utc} · via {stats.provider_name}"
    )

    home_col, away_col = st.columns(2)
    for column, team in ((home_col, stats.home), (away_col, stats.away)):
        with column:
            st.markdown(f"##### {team.name}")
            metric_cols = st.columns(3)
            metric_cols[0].metric("Possession", format_optional(team.possession_pct, suffix="%"))
            metric_cols[1].metric("Shots", format_optional(team.shots))
            metric_cols[2].metric("On target", format_optional(team.shots_on_target))
            detail_cols = st.columns(3)
            detail_cols[0].metric("Corners", format_optional(team.corners))
            detail_cols[1].metric("Yellow", format_optional(team.yellow_cards))
            detail_cols[2].metric("Red", format_optional(team.red_cards))

    st.markdown("##### Event timeline")
    if not stats.events:
        st.caption("No timeline events were returned for this match.")
    else:
        st.dataframe(
            [
                {
                    "Minute": event.minute,
                    "Event": event.event_type,
                    "Team": event.team,
                    "Player": event.player,
                    "Detail": event.detail,
                }
                for event in stats.events
            ],
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()
