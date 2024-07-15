from loguru import logger
from r11data.utils.paths import logs

logger.add(logs / "starlegs.log")

logger.info("Logging from starlegs_log")
