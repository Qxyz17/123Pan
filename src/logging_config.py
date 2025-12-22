# https://github.com/Qxyz17/123pan
# src/logging_config.py

import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging(log_file=None, level=logging.INFO):
    if log_file is None:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, '123pan.log')

    logger = logging.getLogger()
    # Avoid adding multiple handlers in case setup_logging is called more than once
    if logger.handlers:
        return

    logger.setLevel(level)

    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8')
    fh.setFormatter(fmt)
    fh.setLevel(level)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(level)
    logger.addHandler(ch)

    # silence noisy external loggers by default
    logging.getLogger('requests').setLevel(logging.WARNING)


__all__ = ['setup_logging']
