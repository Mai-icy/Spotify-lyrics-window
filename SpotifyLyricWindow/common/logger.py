#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
from logging import Logger

from common.path import ERROR_LOG_PATH


_LOGGER_NAME = "spotify_lyrics_window"
_IS_INITIALIZED = False


def init_logging(level: int = logging.INFO) -> Logger:
    global _IS_INITIALIZED

    logger = logging.getLogger(_LOGGER_NAME)
    if _IS_INITIALIZED:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(ERROR_LOG_PATH, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _IS_INITIALIZED = True
    return logger


def get_logger(name: str) -> Logger:
    init_logging()
    child_name = f"{_LOGGER_NAME}.{name}" if name else _LOGGER_NAME
    return logging.getLogger(child_name)
