import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pluseposter.log"),
    ],
)

logger = logging.getLogger("pluseposter")


def setup_logging(debug: bool = False) -> None:
    """
    Setup logging configuration
    
    Args:
        debug (bool): Enable debug logging
    """
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def validate_file_path(file_path: str) -> Path:
    """
    Validate and return a file path
    
    Args:
        file_path (str): Path to validate
        
    Returns:
        Path: Validated path
        
    Raises:
        ValueError: If file does not exist or is not accessible
    """
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"File does not exist: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    return path


def format_datetime(dt: datetime) -> str:
    """
    Format datetime in ISO format
    
    Args:
        dt (datetime): Datetime to format
        
    Returns:
        str: Formatted datetime string
    """
    return dt.isoformat()
