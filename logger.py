import logging
import os
from datetime import datetime

logging.captureWarnings(True)

#PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
today_str = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = os.path.join(LOG_DIR, f"app-{today_str}.log")

# Set this flag to True when packaging for production
IS_PRODUCTION = False  # Change to False for development


def get_logger(name="app"):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        if IS_PRODUCTION:
            logger.setLevel(logging.ERROR)  # Only log errors
            # return logger
        else:
            logger.setLevel(logging.DEBUG)

            # File handler
            fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
            fh.setLevel(logging.DEBUG)

            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # Formatter
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            logger.addHandler(fh)
            logger.addHandler(ch)
    return logger


logger = get_logger()
