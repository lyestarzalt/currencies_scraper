import logging
import sys
from logging import Logger


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
