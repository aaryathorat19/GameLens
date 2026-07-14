from pathlib import Path

import pytest

from modules.video_upload import UploadValidationError, save_uploaded_video, validate_mp4_upload


class FakeUpload:
    def __init__(self, name: str, content: bytes) -> None:
        self.name = name
        self.size = len(content)
        self._content = content

    def getbuffer(self) -> memoryview:
        return memoryview(self._content)


def test_save_uploaded_video_generates_safe_mp4_name(tmp_path: Path) -> None:
    saved = save_uploaded_video(FakeUpload("final.mp4", b"video"), tmp_path)

    assert saved.parent == tmp_path
    assert saved.suffix == ".mp4"
    assert saved.read_bytes() == b"video"
    assert saved.name != "final.mp4"


def test_validate_mp4_upload_rejects_wrong_extension() -> None:
    with pytest.raises(UploadValidationError, match="MP4"):
        validate_mp4_upload(FakeUpload("match.mov", b"video"))
