import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Create logger
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)

    # Create handlers
    file_handler = RotatingFileHandler(
        'app/logs/app.log',
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