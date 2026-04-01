import json
import logging
import sys

import colorama

from .config import get_settings


class JSONLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger_name": record.name,
            "module": f"{record.module}:{record.lineno}",
            "thread_id": record.thread,
            "thread_name": record.threadName,
            "msg": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ColorConsoleLogFormatter(logging.Formatter):
    COLOR_LEVEL = {
        logging.DEBUG: colorama.Fore.GREEN + colorama.Style.BRIGHT,
        logging.INFO: colorama.Fore.GREEN + colorama.Style.BRIGHT,
        logging.WARNING: colorama.Fore.YELLOW + colorama.Style.BRIGHT,
        logging.ERROR: colorama.Fore.RED + colorama.Style.BRIGHT,
        logging.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT,
    }

    COLOR_MSG = {
        logging.DEBUG: colorama.Fore.BLUE,
        logging.INFO: colorama.Fore.BLUE,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Fore.RED,
    }

    RESET = colorama.Style.RESET_ALL

    def format(self, record: logging.LogRecord) -> str:
        color_level = self.COLOR_LEVEL.get(record.levelno, "")
        color_msg = self.COLOR_MSG.get(record.levelno, "")

        time_str = self.formatTime(record, self.datefmt)
        msg = f"[{time_str}] - {record.name} - {record.module}:{record.lineno} - {color_level}{record.levelname}{self.RESET} - {color_msg}{record.getMessage()}{self.RESET}"

        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            msg += f"\n{colorama.Fore.RED}{exc_text}{self.RESET}"

        return msg


APP_LOGGER_NAME = "app_logger"


def setup_logging():
    settings = get_settings()
    if settings.ENVIRONMENT == "dev":
        log_formatter = ColorConsoleLogFormatter()
        log_level = logging.DEBUG

    else:
        log_formatter = JSONLogFormatter()
        log_level = logging.INFO

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    loggers_to_override = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        APP_LOGGER_NAME,
    ]
    for logger_name in loggers_to_override:
        logger = logging.getLogger(logger_name)

        logger.propagate = False
        logger.setLevel(log_level)

        logger.handlers.clear()
        logger.addHandler(console_handler)


def get_logger() -> logging.Logger:
    return logging.getLogger(APP_LOGGER_NAME)
