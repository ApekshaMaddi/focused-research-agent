from logging.handlers import RotatingFileHandler
import logging
from pathlib import Path


def setup_logging():

    LOG_PATH = (
        Path(__file__).parent.parent.parent.parent
        / "logs"
        / "focused_research_agent.log"
    )
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    py_logger = logging.getLogger()
    py_logger.setLevel(logging.ERROR)

    if py_logger.handlers:
        return py_logger
    else:
        log_handler = RotatingFileHandler(
            filename=LOG_PATH, mode="a", maxBytes=1048576, backupCount=10
        )
        log_formatter = logging.Formatter(
            "%(name)s %(asctime)s %(levelname)s %(message)s"
        )
        log_handler.setFormatter(log_formatter)
        py_logger.addHandler(log_handler)

    return py_logger
