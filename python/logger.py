"""Logger configuration to use ``colorlog.ColoredFormatter``
as the default formatter.

Visit https://pypi.org/project/colorlog/ for more information.
"""

import logging
import os
import socket
from logging.config import dictConfig

STANDARD_FMT = '%(asctime)s | %(levelname)-8s | %(message)s'
COLORED_FMT = '%(log_color)s%(asctime)s%(reset)s | %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'

DOCKER_LOGS_FOLDER = '/usr/logs'
LOCAL_LOGS_FOLDER = '.logs'


def set_logger_conf(on_docker: bool = False):
    path = DOCKER_LOGS_FOLDER if on_docker else LOCAL_LOGS_FOLDER
    file = f'{socket.gethostname()}.log' if on_docker else 'info.log'
    filepath = os.path.join(path, file)

    dictConfig(
        {
            'version': 1,
            'formatters': {
                'standard': {
                    '()': 'logging.Formatter',
                    'fmt': STANDARD_FMT,
                    'datefmt': DATEFMT,
                },
                'colored': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': COLORED_FMT,
                    'datefmt': DATEFMT,
                },
            },
            'handlers': {
                'console': {
                    '()': 'logging.StreamHandler',
                    'formatter': 'colored',
                    'level': logging.DEBUG,
                },
                'file': {
                    'level': 'INFO',
                    'formatter': 'standard',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': filepath,
                    'maxBytes': 104857600,
                    'backupCount': 4,
                    'encoding': 'utf8',
                },
            },
            'root': {
                'handlers': ['console', 'file'],
                'level': logging.DEBUG,
            },
        }
    )


logger = logging.getLogger()
"""Colored logger instance."""
