import logging

from src.core.settings import (
    LOG_LEVEL,
    LOGGING_DATETIME_FORMAT,
    LOGGING_FORMAT,
    PROJECT_NAME,
)

logging.basicConfig(
    level=LOG_LEVEL.upper(), format=LOGGING_FORMAT, datefmt=LOGGING_DATETIME_FORMAT
)

log = logging.getLogger(name=PROJECT_NAME)
