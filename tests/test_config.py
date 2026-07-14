from config import ASSETS_DIR, INPUT_DIR, OUTPUT_DIR, ensure_directories


def test_ensure_directories_creates_runtime_paths() -> None:
    ensure_directories()

    assert INPUT_DIR.is_dir()
    assert OUTPUT_DIR.is_dir()
    assert ASSETS_DIR.is_dir()
