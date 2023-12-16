import logging
import os

logger = logging.getLogger("lab1918")

formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.setLevel(level=os.environ.get("LOG_LEVEL", "INFO").upper())


def config_log_file(logger, filename):
    # for shell user only
    for h in logger.handlers:
        logger.removeHandler(h)

    # create file handler that logs debug and higher level messages
    file_handler = logging.FileHandler(filename, mode="a")
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
