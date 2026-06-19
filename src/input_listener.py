import threading
import sys
from pynput import mouse
from src.models import Target
from src.logger import logger


_click_event = threading.Event()
_last_click: tuple[int, int] = (0, 0)
_listener: mouse.Listener = None


def _on_click(x: int, y: int, button, pressed: bool) -> None:
    global _last_click
    if pressed and button == mouse.Button.left:
        _last_click = (x, y)
        _click_event.set()


def start_listener() -> None:
    """Start the global mouse listener in a background daemon thread."""
    global _listener
    if _listener is not None:
        return  # already started
    # Linux Wayland check (already done in capture, but double-check here)
    if sys.platform.startswith("linux"):
        import os
        session = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if session == "wayland":
            logger.error("Wayland detected. Cannot start mouse listener.")
            return
    _listener = mouse.Listener(on_click=_on_click)
    _listener.start()
    logger.info("Mouse listener started")


def stop_listener() -> None:
    global _listener
    if _listener:
        _listener.stop()
        _listener = None
        logger.info("Mouse listener stopped")


def wait_for_target_click(
    target: Target,
    dpr: float = 1.0,
    timeout: float = None
) -> bool:
    """
    Block until the user clicks INSIDE the target’s logical bounds.
    Both pynput coordinates and the target bounds are in logical pixels,
    so we must convert the target’s PHYSICAL bounds to logical using DPR.
    """
    # Convert physical target bounds to logical bounds for comparison
    logical_x1 = int(target.x1 / dpr)
    logical_y1 = int(target.y1 / dpr)
    logical_x2 = int(target.x2 / dpr)
    logical_y2 = int(target.y2 / dpr)

    # create a temporary logical Target for comparison
    logical_target = Target(
        bbox_id=target.bbox_id,
        x1=logical_x1,
        y1=logical_y1,
        x2=logical_x2,
        y2=logical_y2,
        label=target.label,
        confidence=target.confidence
    )

    _click_event.clear()
    while True:
        if timeout is not None:
            triggered = _click_event.wait(timeout=timeout)
            if not triggered:
                return False
        else:
            _click_event.wait()

        x, y = _last_click
        if logical_target.contains_point(x, y):
            logger.debug(
                f"Valid click at logical ({x},{y}) for target {target.bbox_id}"
            )
            return True
        else:
            logger.debug(f"Click at logical ({x},{y}) outside target, ignoring")
            _click_event.clear()