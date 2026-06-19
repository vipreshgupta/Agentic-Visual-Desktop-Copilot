import sys
import time
import threading
from dotenv import load_dotenv
import keyboard
from PyQt5.QtWidgets import QApplication

from src.logger import logger
from src.input_listener import start_listener, stop_listener
from src.controller import run_copilot_loop

# Global variable to pass the prompt from the hotkey thread to the main GUI thread
pending_prompt = None

def on_hotkey():
    """Callback for when the global hotkey is pressed."""
    global pending_prompt
    print("\n" + "="*50)
    prompt = input("Copilot Triggered! Enter your instruction: ")
    pending_prompt = prompt

def main():
    load_dotenv()
    logger.info("Initializing Agentic Visual Desktop Copilot...")
    
    # Initialize QApplication (required for drawing the red overlay box)
    app = QApplication(sys.argv)
    
    # Start the background mouse click listener
    start_listener()
    
    global pending_prompt
    pending_prompt = None
    
    # Register global hotkey
    hotkey = "ctrl+shift+space"
    keyboard.add_hotkey(hotkey, on_hotkey)
    logger.info(f"Registered hotkey '{hotkey}'. Press it anywhere to activate the Copilot.")
    
    try:
        # Main thread event loop
        # We must keep the main thread running to process GUI events and wait for the hotkey prompt.
        while True:
            if pending_prompt:
                prompt = pending_prompt
                pending_prompt = None
                run_copilot_loop(prompt, app)
                print("\nWaiting for hotkey ('ctrl+shift+space')...")
            
            # Process any pending GUI events
            app.processEvents()
            # Sleep slightly to prevent high CPU usage
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        keyboard.unhook_all()
        stop_listener()
        sys.exit(0)

if __name__ == "__main__":
    main()
