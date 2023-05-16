"""Bolt for Python relies on the standard `logging` module."""

import logging
from logging import Logger
from typing import Any, Optional


def get_bolt_logger(cls: Any, base_logger: Optional[Logger] = None) -> Logger:
    logger = logging.getLogger(f"slack_bolt.{cls.__name__}")
    if base_logger is not None:
        _configure_from_base_logger(logger, base_logger)
    else:
        _configure_from_root(logger)
    return logger


def get_bolt_app_logger(app_name: str, cls: object = None, base_logger: Optional[Logger] = None) -> Logger:
    logger: Logger = (
        logging.getLogger(f"{app_name}:{cls.__name__}") if cls and hasattr(cls, "__name__") else logging.getLogger(app_name)
    )

    if base_logger is not None:
        _configure_from_base_logger(logger, base_logger)
    else:
        _configure_from_root(logger)
    return logger


def _configure_from_base_logger(new_logger: Logger, base_logger: Logger):
    new_logger.disabled = base_logger.disabled
    new_logger.level = base_logger.level
    if len(new_logger.handlers) == 0:
        for h in base_logger.handlers:
            new_logger.addHandler(h)
    if len(new_logger.filters) == 0:
        for f in base_logger.filters:
            new_logger.addFilter(f)


def _configure_from_root(new_logger: Logger):
    new_logger.disabled = logging.root.disabled
    new_logger.level = logging.root.level


__all__ = [
    "get_bolt_logger",
    "get_bolt_app_logger",
]
