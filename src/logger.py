import sys
from pathlib import Path
from loguru import logger

Path("logs").mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stderr,
    level="INFO",
    format="{time:HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
)

logger.add(
    "logs/agent.log",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)

__all__ = ["logger"]