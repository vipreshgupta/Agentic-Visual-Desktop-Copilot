import time
from src.logger import logger
from src.models import Target
from src.capture import capture_primary_monitor_png
from src.parser import parse_screen
from src.groq_client import get_target_from_groq
from src.overlay import OverlayWindow

def run_copilot_loop(user_prompt: str, app=None) -> None:
    """
    Executes one full iteration of the visual copilot loop:
    1. Capture Screen
    2. Parse Elements
    3. LLM Reason
    4. Draw Overlay & Wait for Click
    """
    logger.info(f"Starting copilot loop with prompt: '{user_prompt}'")
    
    # 1. Capture
    screen_data = capture_primary_monitor_png()
    if not screen_data.screenshot_bytes:
        logger.error("Failed to capture screen.")
        return

    # 2. Parse
    parsed_text, coordinates = parse_screen(screen_data.screenshot_bytes)
    if not parsed_text or not coordinates:
        logger.error("Failed to parse screen elements.")
        return

    # 3. LLM Reason
    logger.info("Asking Groq to identify target...")
    target_id_int = get_target_from_groq(user_prompt, parsed_text)
    if target_id_int is None:
        logger.error("LLM failed to select a target.")
        return
        
    target_id = str(target_id_int)
    
    if target_id not in coordinates:
        logger.error(f"Target ID {target_id} returned by LLM is not in coordinates map.")
        return
        
    coords = coordinates[target_id]
    
    # OmniParser returns [cx_ratio, cy_ratio, w_ratio, h_ratio]
    cx_ratio, cy_ratio, w_ratio, h_ratio = coords
    
    cx = cx_ratio * screen_data.width
    cy = cy_ratio * screen_data.height
    w = w_ratio * screen_data.width
    h = h_ratio * screen_data.height
    
    x1 = int(cx - w/2)
    y1 = int(cy - h/2)
    x2 = int(cx + w/2)
    y2 = int(cy + h/2)
    
    target = Target(
        bbox_id=target_id_int,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        label=f"Selected: {target_id}",
        confidence=1.0
    )
    
    logger.info(f"Target selected: ID={target.bbox_id}, bounds={target.bounds}")
    
    # 4. Draw Overlay
    if app is None:
        logger.error("QApplication instance required for overlay.")
        return
        
    overlay = OverlayWindow()
    overlay.signals.show_target.emit(target)
    
    logger.info("Waiting for user to click the target...")
    
    from src.input_listener import _click_event, _last_click
    
    dpr = app.devicePixelRatio()
    logical_target = Target(
        bbox_id=target.bbox_id,
        x1=int(target.x1 / dpr),
        y1=int(target.y1 / dpr),
        x2=int(target.x2 / dpr),
        y2=int(target.y2 / dpr),
        label=target.label,
        confidence=target.confidence
    )
    
    import src.input_listener as input_listener
    input_listener._click_event.clear()
    
    # Custom event loop to keep Qt responsive while waiting for pynput background click
    while True:
        app.processEvents()
        if input_listener._click_event.is_set():
            x, y = input_listener._last_click
            if logical_target.contains_point(x, y):
                logger.info("User clicked the target successfully.")
                break
            else:
                logger.debug(f"Click at ({x}, {y}) ignored, not in target.")
                input_listener._click_event.clear()
        time.sleep(0.01)
        
    overlay.close()
    app.processEvents() # ensure it closes
    logger.info("Copilot loop finished.")
