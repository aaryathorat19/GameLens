"""Streamlit entry point for MatchVision AI."""

import streamlit as st

from config import APP_TAGLINE, APP_TITLE, ensure_directories


def main() -> None:
    ensure_directories()
    st.set_page_config(page_title=APP_TITLE, page_icon="⚽", layout="wide")

    st.title(f"⚽ {APP_TITLE}")
    st.caption(APP_TAGLINE)
    st.info(
        "Project foundation is ready. Video upload and automated highlight generation "
        "will be added in the next milestone."
    )

    st.subheader("How it will work")
    st.markdown(
        "1. Upload a full match recording.\n"
        "2. Detect exciting moments from audio and scene changes.\n"
        "3. Generate, preview, and download your highlights."
    )


if __name__ == "__main__":
    main()
