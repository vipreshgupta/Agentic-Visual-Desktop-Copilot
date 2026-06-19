import os
import re
from typing import Optional
from groq import Groq
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.2-90b-vision-preview")

if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not set in .env")

def get_target_from_groq(prompt: str, parsed_text: str) -> Optional[int]:
    """
    Given a user prompt and the parsed text representations of the screen from OmniParser,
    ask the LLM which element ID to interact with.
    """
    if not GROQ_API_KEY:
        logger.error("Cannot call Groq: GROQ_API_KEY is missing.")
        return None

    # Remove raw bounding box coordinates to drastically save LLM tokens
    parsed_text_clean = re.sub(r"'bbox':\s*\[.*?\],\s*", "", parsed_text)
    
    # Truncate very long 'content' strings to save tokens
    # This finds 'content': '...long text...' and truncates it if it's over ~50 chars
    parsed_text_clean = re.sub(r"('content':\s*')([^']{50})[^']*(',)", r"\1\2...\3", parsed_text_clean)
    
    # Truncate the total string to about 30,000 characters just to be safe from API hard limits
    parsed_text_clean = parsed_text_clean[:30000]

    client = Groq(api_key=GROQ_API_KEY)
    
    system_prompt = (
        "You are a helpful GUI automation assistant. "
        "You will be given a list of parsed UI elements from a desktop screen, "
        "each formatted as 'icon <ID>: <description>'.\n\n"
        "Your job is to identify which element ID the user wants to interact with based on their instruction. "
        "Return ONLY the numeric ID of the chosen element. Do not include any other text, explanation, or punctuation."
    )
    
    user_message = (
        f"User Instruction: {prompt}\n\n"
        f"Parsed Screen Elements:\n{parsed_text_clean}\n\n"
        "Which element ID should I click?"
    )

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0,
            max_tokens=10,
        )
        
        reply = response.choices[0].message.content.strip()
        logger.debug(f"Groq LLM raw reply: {reply}")
        
        # Extract the first number from the reply
        match = re.search(r'\d+', reply)
        if match:
            target_id = int(match.group(0))
            logger.info(f"Groq selected target ID: {target_id}")
            return target_id
        else:
            logger.error(f"Failed to parse ID from Groq reply: {reply}")
            return None
            
    except Exception as e:
        logger.exception(f"Error calling Groq API: {e}")
        return None
