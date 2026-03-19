from logging.handlers import RotatingFileHandler
import logging

def setup_logging():


    py_logger = logging.getLogger()
    py_logger.setLevel(logging.ERROR)

    if py_logger.handlers:
        return py_logger
    else:
        log_handler = RotatingFileHandler(filename="src/logs/focused_research_agent.log", mode='a', maxBytes=2048,
                                                       backupCount=10)
        log_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
        log_handler.setFormatter(log_formatter)
        py_logger.addHandler(log_handler)

    return py_logger