import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Create logger
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = os.path.join('app', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Create handlers with path joining
    log_file = os.path.join(log_dir, 'app.log')
    # Create handlers
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(method)s] %(url)s - Status: %(status)s - Time: %(duration).2fms - %(message)s'
    )
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)

    return logger

# Create a global logger instance
logger = setup_logger()