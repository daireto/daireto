"""Logger configuration to use ``colorlog.ColoredFormatter``
as the default formatter.

Visit https://pypi.org/project/colorlog/ for more information.
"""

import logging
import os
import socket
from logging.config import dictConfig

# Formats
_STANDARD_FMT = '%(asctime)s | %(levelname)-8s | %(message)s'
_COLORED_FMT = '%(log_color)s%(asctime)s%(reset)s | %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s'
_DATEFMT = '%Y-%m-%d %H:%M:%S'

# File rotation
_MAX_BYTES = 100 * 1024 * 1024  # 100 mb
_BACKUP_COUNT = 4
_LOCAL_LOGS_FOLDER = '.logs'
_DOCKER_LOGS_FOLDER = '/usr/logs'


def set_logger_conf(
    file_rotation: bool = False,
    max_bytes: int = _MAX_BYTES,
    backup_count: int = _BACKUP_COUNT,
    local_logs_folder: str = _LOCAL_LOGS_FOLDER,
    on_docker: bool = False,
    docker_logs_folder: str = _DOCKER_LOGS_FOLDER,
) -> None:
    """Sets the logging configuration.

    Parameters
    ----------
    file_rotation : bool, optional
        Whether to add the file rotation handler, by default False.
    max_bytes : int, optional
        Maximum size of each log size, by default _MAX_BYTES.
    backup_count : int, optional
        Maximum number of log files, by default _BACKUP_COUNT.
    local_logs_folder : str, optional
        Path of the local logs folder, by default _LOCAL_LOGS_FOLDER.
    on_docker : bool, optional
        If the program is running on a Docker container,
        by default False.
    docker_logs_folder : str, optional
        Path of the Docker container logs folder,
        by default _DOCKER_LOGS_FOLDER.
    """
    formatters = {
        'standard': {
            '()': 'logging.Formatter',
            'fmt': _STANDARD_FMT,
            'datefmt': _DATEFMT,
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': _COLORED_FMT,
            'datefmt': _DATEFMT,
        },
    }

    handlers = {
        'console': {
            '()': 'logging.StreamHandler',
            'formatter': 'colored',
            'level': logging.DEBUG,
        }
    }

    if file_rotation:
        path = docker_logs_folder if on_docker else local_logs_folder
        os.makedirs(path, exist_ok=True)

        file = f'{socket.gethostname()}.log' if on_docker else 'info.log'
        filepath = os.path.join(path, file)

        handlers['file'] = {
            'level': logging.DEBUG,
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': filepath,
            'maxBytes': max_bytes,
            'backupCount': backup_count,
            'encoding': 'utf8',
        }

    dictConfig(
        {
            'version': 1,
            'formatters': formatters,
            'handlers': handlers,
            'root': {
                'handlers': list(handlers.keys()),
                'level': logging.DEBUG,
            },
        }
    )


logger = logging.getLogger()
"""Colored logger instance."""
