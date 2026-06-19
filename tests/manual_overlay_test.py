import sys
from PyQt5.QtWidgets import QApplication
from src.overlay import OverlayWindow
from src.input_listener import start_listener, stop_listener, wait_for_target_click
from src.models import Target
from src.logger import logger

def main():
    app = QApplication(sys.argv)

    # Create overlay
    overlay = OverlayWindow()
    dpr = overlay._dpr
    logger.info(f"Test using DPR = {dpr}")

    # Get screen geometry (logical pixels)
    screen_geo = QApplication.primaryScreen().availableGeometry()
    screen_w = screen_geo.width()
    screen_h = screen_geo.height()
    logger.info(f"Screen geometry: {screen_w}x{screen_h} (logical)")

    # Create a LARGE target in the CENTER of the screen
    # Target size: 400x300 logical pixels
    target_w = 400
    target_h = 300
    logical_x1 = (screen_w - target_w) // 2
    logical_y1 = (screen_h - target_h) // 2
    logical_x2 = logical_x1 + target_w
    logical_y2 = logical_y1 + target_h

    # Convert to physical coordinates (what the Target expects)
    physical_x1 = int(logical_x1 * dpr)
    physical_y1 = int(logical_y1 * dpr)
    physical_x2 = int(logical_x2 * dpr)
    physical_y2 = int(logical_y2 * dpr)

    target = Target(
        bbox_id=0,
        x1=physical_x1,
        y1=physical_y1,
        x2=physical_x2,
        y2=physical_y2,
        label="CENTER TEST",
        confidence=0.99
    )

    print("\n" + "="*60)
    print("OVERLAY TEST RUNNING")
    print("="*60)
    print(f"Target should appear at center of screen")
    print(f"Logical position: ({logical_x1}, {logical_y1}) to ({logical_x2}, {logical_y2})")
    print(f"Physical position: ({physical_x1}, {physical_y1}) to ({physical_x2}, {physical_y2})")
    print(f"DPR: {dpr}")
    print("\nYou should see a LARGE YELLOW BOX with a black border")
    print("Click INSIDE the yellow box to exit")
    print("="*60 + "\n")

    overlay.signals.show_target.emit(target)

    overlay.signals.show_target.emit(target)

    # Wait for click while processing GUI events
    from src.input_listener import _click_event, _last_click
    _click_event.clear()
    clicked = False
    
    import time
    start_time = time.time()
    while time.time() - start_time < 30.0:
        app.processEvents()
        if _click_event.is_set():
            x, y = _last_click
            # check logical bounds
            if logical_x1 <= x <= logical_x2 and logical_y1 <= y <= logical_y2:
                clicked = True
                break
            _click_event.clear()
        time.sleep(0.01)

    if clicked:
        print("\nSUCCESS: Click detected inside target!")
    else:
        print("\nTIMEOUT: No click detected after 30 seconds")

    stop_listener()
    overlay.close()
    sys.exit(0)

if __name__ == "__main__":
    main()