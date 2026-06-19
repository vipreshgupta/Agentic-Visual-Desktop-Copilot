import os
import json
import tempfile
from dotenv import load_dotenv
from gradio_client import Client, handle_file
from src.logger import logger

load_dotenv()
ENDPOINT = os.getenv("OMNIPARSER_ENDPOINT", "http://127.0.0.1:7861")

def parse_screen(image_bytes: bytes) -> tuple[str, dict]:
    """
    Sends the image to the local OmniParser Gradio server and returns:
    - text_output: str, the parsed elements list
    - coordinates: dict, mapping of ID (str) to [x1, y1, x2, y2]
    """
    logger.info("Sending screen to OmniParser...")
    try:
        client = Client(ENDPOINT)
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name
            
        # The API inputs match gradio_demo.py fn=process
        # outputs match [image_output_component, text_output_component, coordinates_output_component]
        result = client.predict(
            image_input=handle_file(tmp_path),
            box_threshold=0.05,
            iou_threshold=0.1,
            use_paddleocr=False,
            imgsz=640,
            api_name="/process"
        )
        
        os.unlink(tmp_path)
        
        # Result is a tuple: (image_filepath, text_output, coordinates)
        image_out, text_out, coords_out = result
        
        # Save the annotated image for the user to inspect
        os.makedirs("logs", exist_ok=True)
        annotated_path = os.path.join("logs", "annotated_screen.png")
        if os.path.exists(image_out):
            import shutil
            shutil.copy(image_out, annotated_path)
            logger.info(f"Saved annotated screen with all bounding boxes to {annotated_path}")
        
        if isinstance(coords_out, str):
            if os.path.exists(coords_out):
                with open(coords_out, 'r') as f:
                    coords = json.load(f)
            else:
                try:
                    coords = json.loads(coords_out)
                except json.JSONDecodeError:
                    coords = {}
        else:
            coords = coords_out
            
        logger.info(f"Received {len(coords)} parsed elements from OmniParser.")
        return text_out, coords
        
    except Exception as e:
        logger.exception(f"OmniParser error: {e}")
        return "", {}
