import io
import base64
from PIL import Image
from src.logger import logger


def load_png_bytes(png_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(png_bytes)).convert("RGB")


def resize_if_too_large(img: Image.Image, max_dimension: int = 1280) -> Image.Image:
    """
    Resize while preserving aspect ratio only if the image exceeds max_dimension.
    Returns a new PIL.Image.
    """
    if max_dimension <= 0:
        return img
    w, h = img.size
    if max(w, h) <= max_dimension:
        return img
    new_img = img.copy()
    new_img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    return new_img


def compress_for_api(
    png_bytes: bytes,
    max_dimension: int = 1280,
    quality: int = 80
) -> tuple[bytes, int, int]:
    """
    Convert raw PNG bytes to compressed WebP bytes for fast API transmission.
    Returns (webp_bytes, width, height).
    """
    try:
        img = load_png_bytes(png_bytes)
        img = resize_if_too_large(img, max_dimension=max_dimension)
        w, h = img.size

        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=quality, method=4)
        webp = buffer.getvalue()

        logger.debug(
            f"Compressed image to {w}x{h} WebP, {len(webp)/1024:.1f} KB"
        )
        return webp, w, h
    except Exception as e:
        logger.exception(f"Image compression failed: {e}")
        return b"", 0, 0


def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def from_base64(b64: str) -> bytes:
    return base64.b64decode(b64)