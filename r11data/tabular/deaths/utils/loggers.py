"""Loggers for r11tab."""

import importlib.resources
import logging
import logging.handlers


# log_path = importlib.resources.files("r11data.tabular.deaths.logs")
log_path = importlib.resources.files("r11data.logs")
log_file = log_path / "deaths.log"

# formatters
file_formatter = logging.Formatter("%(asctime)s:%(filename)s: %(message)s")
stream_formatter = logging.Formatter("%(levelname)s: %(message)s")

# handlers
rotating_handler = logging.handlers.RotatingFileHandler(
    filename=log_file, maxBytes=2e6, backupCount=1
)
rotating_handler.setLevel(logging.WARNING)
rotating_handler.setFormatter(file_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(stream_formatter)


class LTWarningFilter(logging.Filter):
    """Filter for skipping log levels lower than warning."""

    def filter(self, record):  # noqa: D102
        return record.levelno < logging.WARNING


stream_handler.addFilter(LTWarningFilter())

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)
logger.addHandler(stream_handler)
