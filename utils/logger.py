import logging
from typing import Optional


def configure_logger(name: str = "automation", level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a module-level logger.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a child logger from the configured root.
    """
    root = configure_logger()
    return root.getChild(name) if name else root
