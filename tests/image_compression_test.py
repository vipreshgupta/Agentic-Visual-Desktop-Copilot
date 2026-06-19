from pathlib import Path
from src.capture import capture_primary_monitor_png
from src.image_utils import compress_for_api, to_base64

PNG_PATH = Path("logs") / "last_capture.png"
WEBP_PATH = Path("logs") / "last_compressed.webp"


def main():
    PNG_PATH.parent.mkdir(exist_ok=True)

    data = capture_primary_monitor_png()
    PNG_PATH.write_bytes(data.screenshot_bytes)

    webp, w, h = compress_for_api(data.screenshot_bytes, max_dimension=1280, quality=80)
    if not webp:
        raise RuntimeError("Compression returned empty bytes")
    WEBP_PATH.write_bytes(webp)

    b64 = to_base64(webp)
    print(f"Original PNG: {len(data.screenshot_bytes)/1024:.1f} KB")
    print(f"Compressed WebP: {len(webp)/1024:.1f} KB, size={w}x{h}")
    print(f"Base64 length: {len(b64)}")
    print(f"Saved {PNG_PATH} and {WEBP_PATH}")

if __name__ == "__main__":
    main()