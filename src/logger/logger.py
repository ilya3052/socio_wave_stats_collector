import logging
import os
from logging.config import dictConfig

LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'

os.makedirs(os.path.dirname(LOG_FILE) or '.', exist_ok=True)


class FileFormatter(logging.Formatter):
    def format(self, record):
        # Базовая строка лога
        log_message = super().format(record)

        # Если есть исключение — добавляем traceback
        if record.exc_info:
            log_message += "\n" + self.formatException(record.exc_info)

        return log_message


class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        exc_info = record.exc_info
        record.exc_info = None
        log_message = super().format(record)
        record.exc_info = exc_info
        return log_message


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": ConsoleFormatter,
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        },
        "file": {
            "()": FileFormatter,
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": LOG_LEVEL,
            "formatter": "file",
            "filename": LOG_FILE,
            "maxBytes": 10_485_760,
            "backupCount": 5,
            "encoding": "utf-8",
            "delay": True,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "src": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    }
}


def configure_logging():
    dictConfig(LOGGING_CONFIG)
    logging.getLogger().info(f"Система логирования запущена с уровнем {LOG_LEVEL}")
