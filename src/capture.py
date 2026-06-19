import os
import sys
import time
import mss
import mss.tools

from src.logger import logger
from src.models import ScreenData


def _check_linux_wayland() -> bool:
    """
    Version 1.0 does not support Wayland because global screen capture
    and input tracking are restricted there.
    """
    if sys.platform.startswith("linux"):
        session_type = (os.environ.get("XDG_SESSION_TYPE") or "").lower()
        if session_type == "wayland":
            logger.error(
                "Wayland detected. Version 1.0 does NOT support Wayland. "
                "Please switch to X11 / Xorg."
            )
            return False
    return True


def capture_primary_monitor_png() -> ScreenData:
    """
    Capture the PRIMARY monitor only and return PNG bytes.

    Important:
    - Coordinates are in PHYSICAL pixels.
    - Version 1.0 supports single-monitor usage only.
    """
    if not _check_linux_wayland():
        return ScreenData(
            screenshot_bytes=b"",
            width=0,
            height=0,
            timestamp=time.time(),
        )

    start = time.perf_counter()

    try:
        with mss.mss() as sct:
            real_monitor_count = len(sct.monitors) - 1

            if real_monitor_count <= 0:
                logger.error("No monitors detected by mss.")
                return ScreenData(
                    screenshot_bytes=b"",
                    width=0,
                    height=0,
                    timestamp=time.time(),
                )

            if real_monitor_count > 1:
                logger.warning(
                    f"Multiple monitors detected ({real_monitor_count}). "
                    "Version 1.0 supports ONLY the primary monitor. "
                    "Move the target application to the primary display."
                )

            # mss.monitors[1] = primary monitor
            monitor = sct.monitors[1]
            shot = sct.grab(monitor)

            width, height = shot.size
            png_bytes = mss.tools.to_png(shot.rgb, shot.size)

            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info(
                f"Screen captured successfully: {width}x{height} "
                f"in {elapsed_ms:.1f} ms"
            )

            return ScreenData(
                screenshot_bytes=png_bytes,
                width=width,
                height=height,
                monitor_left=monitor["left"],
                monitor_top=monitor["top"],
                monitor_width=monitor["width"],
                monitor_height=monitor["height"],
                timestamp=time.time(),
            )

    except Exception as e:
        logger.exception(f"Screen capture failed: {e}")
        return ScreenData(
            screenshot_bytes=b"",
            width=0,
            height=0,
            timestamp=time.time(),
        )