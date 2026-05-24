"""Unit tests for shared/utils/image_validation.py."""

import pytest

from shared.utils.image_validation import validate_image_magic_bytes

# ── Real magic byte prefixes ───────────────────────────────────────────────

JPEG_MAGIC = b"\xff\xd8\xff" + b"\x00" * 20
PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
WEBP_MAGIC = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"\x00" * 20

# A plausible payload a malicious client might send.
FAKE_JPEG = b"PK\x03\x04" + b"\x00" * 20  # zip file header

# Truncated — too short to validate.
TOO_SHORT = b"\xff\xd8"


@pytest.mark.parametrize(
    "data, content_type, expected",
    [
        (JPEG_MAGIC, "image/jpeg", True),
        (PNG_MAGIC, "image/png", True),
        (WEBP_MAGIC, "image/webp", True),
        # Content-Type correct but bytes are wrong.
        (FAKE_JPEG, "image/jpeg", False),
        (JPEG_MAGIC, "image/png", False),
        (PNG_MAGIC, "image/webp", False),
        # Unrecognised type.
        (JPEG_MAGIC, "image/gif", False),
        # Truncated file.
        (TOO_SHORT, "image/jpeg", False),
        # Empty.
        (b"", "image/jpeg", False),
    ],
)
def test_validate_image_magic_bytes(data: bytes, content_type: str, expected: bool):
    assert validate_image_magic_bytes(data, content_type) is expected
