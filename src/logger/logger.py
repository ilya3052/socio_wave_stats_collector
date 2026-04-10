import logging
import os
from datetime import datetime
from logging.config import dictConfig

LOG_LEVEL = 'INFO'

def get_log_file(log_type: str = 'system') -> str:
    log_type = log_type.lower()
    today = datetime.now().strftime("%Y-%m-%d")
    if log_type == 'vk':
        base_dir = 'logs/vk'
        filename = f'vk_{today}.log'
    elif log_type == 'tg':
        base_dir = 'logs/tg'
        filename = f'tg_{today}.log'
    else:
        base_dir = 'logs/system'
        filename = f'system_{today}.log'

    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, filename)


class FileFormatter(logging.Formatter):
    def format(self, record):
        log_message = super().format(record)
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


def configure_logging(log_type: str = 'system'):
    log_file = get_log_file(log_type)
    os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)

    LOGGING_CONFIG['handlers']['file']['filename'] = log_file

    dictConfig(LOGGING_CONFIG)
    logging.getLogger().info(
        f"Система логирования запущена с уровнем {LOG_LEVEL}. "
        f"Файл: {log_file} (тип: {log_type})"
    )
