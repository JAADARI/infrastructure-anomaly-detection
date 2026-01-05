import logging
import logging.handlers
import os
from datetime import datetime

def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configure and return a logger instance with file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # File handler with rotation
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger