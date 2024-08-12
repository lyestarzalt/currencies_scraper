import logging
import sys
from logging import Logger

def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    
    # Clear any existing handlers if they exist to prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set the logger level
    logger.setLevel(logging.DEBUG)

    # Create a stream handler that outputs to stdout
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.DEBUG)

    # Set the formatter for the handler
    c_format = logging.Formatter(
        "%Y-%m-%d %H:%M:%S - %(name)s - %(levelname)s - %(message)s"
    )
    c_handler.setFormatter(c_format)

    # Add the handler to the logger
    logger.addHandler(c_handler)

    return logger
