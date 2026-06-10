"""Helpers for storing uploaded site images."""

from pathlib import Path

from app.utils.exceptions import BadRequestError

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def save_replaced_image(
    content: bytes,
    content_type: str | None,
    directory: Path,
    file_stem: str,
    public_prefix: str,
) -> str:
    """Save an image under a stable id-based name and remove old variants."""

    extension = ALLOWED_IMAGE_TYPES.get((content_type or "").split(";")[0].lower())
    if extension is None:
        raise BadRequestError("Можно загрузить только изображение jpg, png, webp или gif")
    if not content:
        raise BadRequestError("Файл изображения пустой")
    if len(content) > MAX_IMAGE_SIZE:
        raise BadRequestError("Изображение должно быть не больше 5 МБ")

    directory.mkdir(parents=True, exist_ok=True)
    for old_file in directory.glob(f"{file_stem}.*"):
        old_file.unlink(missing_ok=True)

    filename = f"{file_stem}{extension}"
    (directory / filename).write_bytes(content)
    return f"{public_prefix}/{filename}"
