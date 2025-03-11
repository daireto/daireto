"""Logger configuration to use ``colorlog.ColoredFormatter``
as the default formatter.

Requires: Python 3.6+

Install: ``pip install colorlog``

Visit https://pypi.org/project/colorlog/ for more information.
"""

import logging
from logging.config import dictConfig

FMT = "%(log_color)s%(asctime)s | %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

dictConfig(
    {
        'version': 1,
        'formatters': {
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'format': FMT,
                'datefmt': DATE_FMT,
            }
        },
        'handlers': {
            'console': {
                '()': 'logging.StreamHandler',
                'formatter': 'colored',
                'level': logging.DEBUG,
            },
            # 'file': {
            #     '()': 'logging.handlers.RotatingFileHandler',
            #     'filename': 'log.log',
            #     'formatter': 'colored',
            #     'level': logging.DEBUG,
            #     'maxBytes': 1024 * 1024 * 5,  # 5 MB
            #     'backupCount': 2,
            #     'encoding': 'utf-8',
            # },
        },
        'root': {
            'handlers': ['console'],
            'level': logging.DEBUG,
        },
    }
)

logger = logging.getLogger()
"""Colored logger instance."""
