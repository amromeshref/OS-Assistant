import logging
import logging.config
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

# Log file location
LOG_PATH = Path("logs/os_assistant.log")
SEPARATOR_LENGTH = 50  # Length of the === line


class InfoFilter(logging.Filter):
    """Allow only INFO level logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == logging.INFO


def setup_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "only_info": {
                "()": InfoFilter,
            }
        },
        "formatters": {
            "simple": {
                "format": "%(levelname)s: %(message)s",
            },
            "detailed": {
                "format": "[%(levelname)s|%(name)s|%(filename)s:%(lineno)d] %(asctime)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            # INFO → stdout
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "simple",
                "filters": ["only_info"],
            },
            # WARNING+ → stderr
            "stderr": {
                "class": "logging.StreamHandler",
                "stream": sys.stderr,
                "formatter": "simple",
                "level": "WARNING",
            },
            # File logging (all levels)
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(LOG_PATH),
                "formatter": "detailed",
                "level": "DEBUG",
                "maxBytes": 5 * 1024 * 1024,  # 5 MB
                "backupCount": 2,
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["stdout", "stderr", "file"],
        },
    }

    logging.config.dictConfig(logging_config)

    # Add start separator automatically
    logger = get_logger("os_assistant")
    log_separator(logger, note="START")


def get_logger(name: str = "os_assistant") -> logging.Logger:
    """Return a logger by name."""
    return logging.getLogger(name)


def log_separator(
    logger: logging.Logger, length: int = SEPARATOR_LENGTH, note: str = ""
) -> None:
    """Logs a separator line with optional note."""
    line = "=" * length
    if note:
        line = f"{line} {note} {line}"
    logger.info(line)


def log_session_end():
    """Call this at the end of a session to log a separator."""
    logger = get_logger("os_assistant")
    log_separator(logger, note="END")


setup_logging()
