from pathlib import Path

from src.capture import capture_primary_monitor_png
from src.logger import logger


def main() -> None:
    Path("logs").mkdir(exist_ok=True)

    screen_data = capture_primary_monitor_png()

    if not screen_data.screenshot_bytes:
        raise RuntimeError("Capture failed: screenshot bytes are empty.")

    output_path = Path("logs") / "last_capture.png"
    output_path.write_bytes(screen_data.screenshot_bytes)

    logger.info(f"Saved screenshot to: {output_path.resolve()}")
    logger.info(
        f"Captured size: {screen_data.width}x{screen_data.height}, "
        f"bytes={len(screen_data.screenshot_bytes)}"
    )


if __name__ == "__main__":
    main()