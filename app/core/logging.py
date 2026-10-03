"""Logging configuration.

Human-readable, structured-enough logs: timestamp, level, logger, message.
No external logging platform is used. Secrets, tokens, and document
contents must never be passed to log calls.
"""

import logging
import logging.config

from app.core.config import Settings

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def setup_logging(settings: Settings) -> None:
    """Configure the root logger for the application."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {"format": LOG_FORMAT, "datefmt": DATE_FORMAT},
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stderr",
                },
            },
            "root": {
                "level": settings.log_level.upper(),
                "handlers": ["default"],
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger (thin convenience wrapper)."""
    return logging.getLogger(name)
