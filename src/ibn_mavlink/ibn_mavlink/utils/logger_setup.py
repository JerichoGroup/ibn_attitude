"""Logger setup utilities."""

import logging
from logging import StreamHandler, FileHandler
from pathlib import Path


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Create a logger that outputs to both stdout and a file.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)

        # Create parent directory if missing
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        file_handler = FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger