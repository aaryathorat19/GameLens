"""Central configuration for GameLens."""

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"

load_dotenv(PROJECT_ROOT / ".env")

APP_TITLE = "GameLens"
APP_TAGLINE = "AI Football Highlight Generator & Match Analyzer"
MAX_UPLOAD_SIZE_MB = 500
API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
STATS_HTTP_TIMEOUT_SECONDS = 10.0


def ensure_directories() -> None:
    """Create runtime directories required by the application."""
    for directory in (INPUT_DIR, OUTPUT_DIR, ASSETS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
