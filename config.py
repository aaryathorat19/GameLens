"""Central configuration for MatchVision AI."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"

APP_TITLE = "MatchVision AI"
APP_TAGLINE = "AI Football Highlight Generator & Match Analyzer"
MAX_UPLOAD_SIZE_MB = 500


def ensure_directories() -> None:
    """Create runtime directories required by the application."""
    for directory in (INPUT_DIR, OUTPUT_DIR, ASSETS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
