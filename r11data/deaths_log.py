from loguru import logger
from r11data.utils.paths import logs

logger.add(logs / "_deaths.log")

logger.info("Logging from deaths_log")
