"""
Storage key utilities.

Centralises logic for extracting S3 object keys from public URLs so
services don't import concrete classes from sibling services.
"""


def extract_avatar_key(url: str) -> str:
    """
    Extract the S3 object key from a full avatar URL.

    Walks the URL path from the first 'avatars/' segment to the end.
    If the sentinel is absent (e.g. an externally-set URL), returns the
    original URL unchanged — the caller should handle or log the outcome.

    Examples:
        >>> extract_avatar_key(
        ...     "https://bucket.s3.amazonaws.com/avatars/abc/photo.jpg"
        ... )
        'avatars/abc/photo.jpg'

        >>> extract_avatar_key("https://external.example.com/photo.jpg")
        'https://external.example.com/photo.jpg'
    """
    parts = url.split("/")
    avatar_index = next(
        (i for i, p in enumerate(parts) if p == "avatars"), None
    )
    if avatar_index is None:
        return url
    return "/".join(parts[avatar_index:])
