"""Shared validation helpers."""

import re

from app.utils.exceptions import BadRequestError


TAG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$")


def normalize_tag_name(name: str) -> str:
    """Normalize and validate a tag name."""

    normalized = name.strip().lower().replace(" ", "-")
    if not TAG_RE.fullmatch(normalized):
        raise BadRequestError("Tag names must be 3-40 chars: letters, digits, hyphens")
    return normalized


def ensure_text(value: str, field_name: str) -> str:
    """Ensure a text field is not blank after stripping whitespace."""

    stripped = value.strip()
    if not stripped:
        raise BadRequestError(f"{field_name} must not be blank")
    return stripped
