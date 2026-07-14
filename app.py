"""Streamlit entry point for MatchVision AI."""

from pathlib import Path

import streamlit as st

from config import APP_TAGLINE, APP_TITLE, ensure_directories
from modules.video_upload import UploadValidationError, save_uploaded_video
from services.audio_extractor import AudioExtractionError, extract_audio, ffmpeg_available


def main() -> None:
    ensure_directories()
    st.set_page_config(page_title=APP_TITLE, page_icon="football", layout="wide")

    st.title(APP_TITLE)
    st.caption(APP_TAGLINE)
    st.info("Phase 2: upload a match recording and prepare its audio track.")

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

    st.subheader("How it will work")
    st.markdown(
        "1. Upload a full match recording.\n"
        "2. Prepare its audio track.\n"
        "3. Detect exciting moments and generate highlights in the next phases."
    )


if __name__ == "__main__":
    main()
