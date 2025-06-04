"""Logger configuration.

Install loguru with:
    pip install loguru
"""

import sys
from datetime import time, timedelta
from pathlib import Path

from loguru import logger


def setup_logger(
    level: str | int = 'INFO',
    fmt: str | None = None,
    alignment_width: int = 8,
    backtrace: bool = False,
    diagnose: bool = False,
    enqueue: bool = False,
    colorize: bool = False,
    use_file: bool = False,
    rotation: str | int | time | timedelta | None = None,
    retention: str | int | timedelta | None = None,
    filename: str | None = None,
    dst: str = '.logs',
    docker_dst: str = '/var/log/app',
    on_docker: bool = False,
) -> None:
    """Sets up logger.

    Parameters
    ----------
    level : str | int, optional
        Logger level, by default 'INFO'.
    fmt : str | None, optional
        Format, by default None.
    alignment_width : int, optional
        Alignment width of the level name, by default 8.
        Used only with the default format (if ``fmt`` is None).
    backtrace : bool, optional
        Whether to show backtrace, by default False.
    diagnose : bool, optional
        Whether to show diagnose. Be careful with this,
        as it may leak sensitive information. By default False.
    enqueue : bool, optional
        Whether to enqueue the messages to ensure logs integrity,
        by default False.
    colorize : bool, optional
        Whether to colorize the output, by default False.
    use_file : bool, optional
        Whether to add a file handler, by default False.
    rotation : str | int | time | timedelta | None, optional
        The rotation to use if ``use_file`` is True,
        for example '10 MB', by default None.
        Visit the `loguru documentation <https://loguru.readthedocs.io/en/stable/overview.html#easier-file-logging-with-rotation-retention-compression>`_
        for more information.
    retention : str | int | timedelta | None, optional
        The retention to use for rotated files if ``use_file`` is True,
        for example '10 days', by default None.
    filename : str | None, optional
        Filename to use if ``use_file`` is True, by default None.
        If None, it will be set to ``main.log``.
    dst : str, optional
        Destination folder to use if ``use_file`` is True and
        ``on_docker`` is False, by default '.logs'.
    docker_dst : str, optional
        Destination folder to use if ``use_file`` is True and
        ``on_docker`` is True, by default '/var/log/app'.
    on_docker : bool, optional
        Whether the app is running on docker, by default False.

    Examples
    --------
    >>> setup_logger(level='DEBUG')
    >>> logger.debug('debug')
    2025-05-05 11:46:36 | DEBUG    | __main__:<module>:1 - debug
    >>> setup_logger(fmt='<level>{message}</level>')
    >>> logger.info('info')
    info
    """
    logger.remove()

    fmt = (
        fmt
        or (
            '<green>{time:YYYY-MM-DD HH:mm:ss}</green>'
            ' | <level>{level: <%d}</level>'
            ' | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>'
            ' - <level>{message}</level>'
        )
        % alignment_width
    )

    logger.add(
        sink=sys.stderr,
        level=level,
        format=fmt,
        backtrace=backtrace,
        diagnose=diagnose,
        enqueue=enqueue,
        colorize=colorize,
    )

    if use_file:
        filepath = (filename or 'main.log').strip()

        dst = (docker_dst if on_docker else dst).strip()
        if dst:
            Path(dst).mkdir(parents=True, exist_ok=True)
            filepath = Path(dst) / filepath

        logger.add(
            filepath,
            level=level,
            format=fmt,
            rotation=rotation,
            retention=retention,
            backtrace=backtrace,
            diagnose=diagnose,
            enqueue=enqueue,
            colorize=colorize,
        )


setup_logger()
