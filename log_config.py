import logging
from config import LOG_LEVEL, LOG_FORMAT

def setup_logging():
    """Configure logging for the application"""
    # Convert string log level to logging constant
    numeric_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Configure the root logger
    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler()  # Log to console
        ]
    )
    
    # Set more restrictive logging for some chatty libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.debug("Logging configured successfully")
