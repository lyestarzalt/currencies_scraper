import logging
import sys
from logging import Logger

def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setLevel(logging.DEBUG)

        c_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        c_handler.setFormatter(c_format)

        logger.addHandler(c_handler)

    logger.propagate = True

    return logger
