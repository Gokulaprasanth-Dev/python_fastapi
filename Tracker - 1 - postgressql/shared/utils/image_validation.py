"""
Image file signature (magic byte) validation.

Content-Type headers are client-controlled and trivially spoofed.
This module validates the actual file bytes against known image signatures
so a file named "exploit.exe" with Content-Type: image/jpeg is rejected.

Supported formats and their magic bytes:
  JPEG  — FF D8 FF
  PNG   — 89 50 4E 47 0D 0A 1A 0A  (\\x89PNG\\r\\n\\x1a\\n)
  WebP  — 52 49 46 46 .. .. .. .. 57 45 42 50  (RIFF....WEBP)

Only the minimum prefix needed for unambiguous identification is checked.
"""

# Maps MIME type → (offset, magic_bytes) pairs.
# offset is where in the file the magic bytes start (always 0 here, but
# kept explicit so it's easy to add formats like TIFF that use offsets).
_SIGNATURES: dict[str, tuple[int, bytes]] = {
    "image/jpeg": (0, b"\xff\xd8\xff"),
    "image/png": (0, b"\x89PNG\r\n\x1a\n"),
    "image/webp": (0, b"RIFF"),  # see _is_webp for the secondary check
}

# Minimum bytes needed to identify any supported format.
_MIN_BYTES = 12  # enough for RIFF....WEBP (12 bytes)


def _is_webp(data: bytes) -> bool:
    """
    WebP files start with RIFF followed by 4 length bytes then WEBP.
    We check both anchors to avoid misidentifying other RIFF containers
    (e.g. WAV, AVI).
    """
    return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"


def validate_image_magic_bytes(data: bytes, content_type: str) -> bool:
    """
    Return True if *data* starts with the magic bytes expected for
    *content_type*.  Return False if the bytes don't match — the caller
    should raise an appropriate error.

    Args:
        data:         The raw file bytes (at least _MIN_BYTES long).
        content_type: The MIME type declared by the client, e.g. "image/jpeg".

    Returns:
        True  — bytes match the declared type.
        False — mismatch or unrecognised type.
    """
    if len(data) < _MIN_BYTES:
        return False

    if content_type == "image/webp":
        return _is_webp(data)

    entry = _SIGNATURES.get(content_type)
    if entry is None:
        return False

    offset, magic = entry
    return data[offset: offset + len(magic)] == magic
