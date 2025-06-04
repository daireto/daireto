"""Utils."""

import hashlib
import os
import re
import time
import unicodedata
from collections.abc import Callable, Sequence
from datetime import timedelta
from functools import wraps
from typing import overload

import psutil
from loguru import logger
from pandas import DataFrame, Index, Series


class ExternalReadingError(Exception):
    pass


class InvalidTruthValueError(Exception):
    """Not a valid boolean representation."""

    def __init__(self, value: str) -> None:
        """Create an instance of this error.

        Parameters
        ----------
        value : str
            The invalid value.

        """
        super().__init__(f'invalid truth value: {value!r}')


def memory_consumption(func: Callable) -> Callable:
    """Decorator to measure memory consumption of a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024
        result = func(*args, **kwargs)
        mem_after = process.memory_info().rss / 1024 / 1024
        mem_consumption = mem_after - mem_before
        GB = 1024 * 1024
        if mem_consumption < GB:
            logger.info(
                f'Consumo de memoria de {func.__qualname__}:'
                f' {mem_consumption:.2f} MB'
            )
        elif mem_consumption >= GB:
            logger.warning(
                f'Consumo de memoria de {func.__qualname__}:'
                f' {mem_consumption / GB:.2f} GB'
            )
        return result

    return wrapper


def timer(func: Callable) -> Callable:
    """Decorator to measure execution time of a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        prettified = str(timedelta(seconds=execution_time))
        prettified_minutes = prettified.split(':', 1)[-1].split('.')[0]
        logger.info(
            f'Tiempo de ejecución de {func.__qualname__}:'
            f' {execution_time:.2f} segundos, {prettified_minutes} minutos'
        )
        return result

    return wrapper


def sha256sum(filepath: str) -> str:
    """Calculates SHA256 checksum.

    Parameters
    ----------
    filepath : str
        File path.

    Returns
    -------
    str
        SHA256 checksum.
    """
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filepath, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def file_has_changed(filepath: str, replace_checksum=False) -> bool:
    """Checks if file has changed. Writes checksum to file.

    If `replace_checksum` is True, replaces checksum.

    Parameters
    ----------
    filepath : str
        File path.
    replace_checksum : bool, optional
        Replace checksum, by default False.

    Returns
    -------
    bool
        True if file has changed, False otherwise.
    """
    filename = os.path.basename(filepath)
    checksum_filename = f'{filename}.sha256sum.txt'
    checksum_path = os.path.join(os.path.dirname(filepath), checksum_filename)

    if not os.path.exists(checksum_path):
        with open(checksum_path, 'w+') as f:
            f.write(sha256sum(filepath))
        return True

    with open(checksum_path, 'r+') as f:
        checksum = f.read()
        changed = checksum != sha256sum(filepath)
        if changed and replace_checksum:
            f.seek(0)
            f.truncate()
            f.write(sha256sum(filepath))

    return changed


def extract_digits(value: str | Series) -> str | Series:
    """Extracts digits from `value`.

    Parameters
    ----------
    value : str | Series
        Source.

    Returns
    -------
    str | Series
        Found digits.

    Examples
    --------
    >>> extract_digits('abc123')
    '123'
    >>> extract_digits('abc')
    ''
    """
    if isinstance(value, Series):
        return value.astype(str).replace(r'\D', '', regex=True).str.lstrip('0')

    return re.sub(r'\D', '', value).lstrip('0')


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1';
    false values are 'n', 'no', 'f', 'false', 'off', and '0'.

    Parameters
    ----------
    val : str
        The string to convert.

    Returns
    -------
    bool
        The boolean representation of `val`.

    Raises
    ------
    ValueError
        If the string is not a valid boolean representation.

    Examples
    --------
    >>> strtobool('YES')
    True
    >>> strtobool('yes')
    True
    >>> strtobool('no')
    False
    >>> strtobool('1')
    True
    >>> strtobool('0')
    False
    >>> strtobool('true')
    True
    >>> strtobool('false')
    False
    >>> strtobool('invalid')
    Traceback (most recent call last):
        ...
    InvalidTruthValueError: invalid truth value: 'invalid'

    """
    val = val.lower().strip()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    if val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    raise InvalidTruthValueError(val)


def normalize_string(text: str) -> str:
    """Normalizes a string by converting non-word characters
    to underscores, converting accented characters to ASCII,
    and transforming to uppercase.

    Parameters
    ----------
    text : str
        String to normalize.

    Returns
    -------
    str
        Normalized string.

    Examples
    --------
    >>> normalize_string('Héllo Wórld!')
    'HELLO_WORLD_'
    >>> normalize_string('áéíóúÁÉÍÓÚñÑ')
    'AEIOUAEIOUNN'
    >>> normalize_string('user@example.com')
    'USER_EXAMPLE_COM'
    """
    text = text.replace(' ', '')
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    text = re.sub(r'\W', '_', text)
    return text.upper()


@overload
def normalize_series(array: Series) -> Series: ...


@overload
def normalize_series(array: Index) -> Index: ...


def normalize_series(array: Series | Index) -> Series | Index:
    """Normalizes a pandas ``Series`` by converting non-word characters
    to underscores, converting accented characters to ASCII,
    and transforming all strings to uppercase.

    Parameters
    ----------
    array : Series | Index
        Array to be normalized.

    Returns
    -------
    Series | Index
        Normalized array.

    Examples
    --------
    >>> import pandas as pd
    >>> series = pd.Series(['Héllo', 'Wórld!', 'user@example.com'])
    >>> series_normalize(series)
    0               HELLO
    1              WORLD_
    2    USER_EXAMPLE_COM
    dtype: object
    """
    return (
        array.astype(str)
        .str.replace(' ', '')
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .str.replace(r'\W', '_', regex=True)
        .str.upper()
    )


def series_equal_to(
    array: Series, value: str | Series, normalize_value: bool = True
) -> Series:
    """Compares a pandas ``Series`` with a value.

    Parameters
    ----------
    array : Series
        Array to be compared.
    value : str | Series
        Value to compare with.
    normalize_value : bool, optional
        Normalize value, by default True.

    Returns
    -------
    Series
        Boolean Series with the comparison result.

    Examples
    --------
    >>> import pandas as pd
    >>> series = pd.Series(['hello', 'world'])
    >>> series_equal_to(series, 'hello')
    0     True
    1    False
    dtype: bool
    """
    if normalize_value:
        return array == (
            normalize_string(value)
            if isinstance(value, str)
            else normalize_series(value)
        )

    return array == value


def series_not_equal_to(
    array: Series, value: str | Series, normalize_value: bool = True
) -> Series:
    """Compares a pandas ``Series`` with a value.

    Parameters
    ----------
    array : Series
        Array to be compared.
    value : str | Series
        Value to compare with.
    normalize_value : bool, optional
        Normalize value, by default True.

    Returns
    -------
    Series
        Boolean Series with the comparison result.

    Examples
    --------
    >>> import pandas as pd
    >>> series = pd.Series(['hello', 'world'])
    >>> series_not_equal_to(series, 'hello')
    0    False
    1     True
    dtype: bool
    """
    if normalize_value:
        return array != (
            normalize_string(value)
            if isinstance(value, str)
            else normalize_series(value)
        )

    return array != value


def series_isin(
    array: Series,
    values: Series | Sequence[str],
    normalize_value: bool = True,
) -> Series:
    """Compares a pandas ``Series`` with a list of values.

    Parameters
    ----------
    array : Series
        Array to be compared.
    values : Series | Sequence[str]
        Series or sequence of values to compare with.
    normalize_value : bool, optional
        Normalize values, by default False.

    Returns
    -------
    Series
        Boolean Series with the comparison result.

    Examples
    --------
    >>> import pandas as pd
    >>> series = pd.Series(['hello', 'world', 'foo'])
    >>> series_isin(series, ['hello', 'world'])
    0     True
    1     True
    2    False
    dtype: bool
    """
    if normalize_value:
        if isinstance(values, Series):
            values = normalize_series(values)
        else:
            values = [normalize_string(v) for v in values]

    return array.isin(values)


def series_contains(
    array: Series,
    value: str | Sequence[str],
    regex: bool = False,
    normalize_value: bool = True,
) -> Series:
    """Compares a pandas ``Series`` with a value.

    Parameters
    ----------
    array : Series
        Array to be compared.
    value : str | Sequence[str]
        Value to compare with.
    regex : bool, optional
        Whether to use regular expressions, by default False.
    normalize_value : bool, optional
        Normalize value, by default True.

    Returns
    -------
    Series
        Boolean Series with the comparison result.

    Examples
    --------
    >>> import pandas as pd
    >>> series = pd.Series(['hello', 'world'])
    >>> series_contains(series, 'llo')
    0     True
    1    False
    dtype: bool
    """
    if not isinstance(value, str):
        value = '|'.join(
            [normalize_string(v) if normalize_value else v for v in value]
        )

    return array.astype(str).str.contains(
        value if regex or not normalize_value else normalize_string(value),
        regex=regex,
    )


def upper_strip_series(array: Series) -> Series:
    """Transforms a pandas ``Series`` to uppercase
    removing leading and trailing whitespaces.

    Parameters
    ----------
    array : Series
        Array to be transformed.

    Returns
    -------
    Series
        Transformed array.

    Examples
    --------
    >>> import pandas as pd
    >>> series = pd.Series(['hello', 'world'])
    >>> series_upper_strip(series)
    0    HELLO
    1    WORLD
    dtype: object
    """
    return array.astype(str).str.strip().str.upper()


def strip_columns(df: DataFrame) -> DataFrame:
    """Removes leading and trailing whitespaces from column names.

    Parameters
    ----------
    df : DataFrame
        DataFrame to be transformed.

    Returns
    -------
    DataFrame
        Transformed DataFrame.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'col1 ': [1, 2], ' col2': [3, 4]})
    >>> df.columns
    Index(['col1 ', ' col2'], dtype='object')
    >>> strip_columns(df).columns
    Index(['col1', 'col2'], dtype='object')
    """
    df.columns = df.columns.astype(str).str.strip()
    return df


def normalize_columns(df: DataFrame) -> DataFrame:
    """Normalizes column names.

    Parameters
    ----------
    df : DataFrame
        DataFrame to be transformed.

    Returns
    -------
    DataFrame
        Transformed DataFrame.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'col1 ': [1, 2], ' col2': [3, 4]})
    >>> df.columns
    Index(['col1 ', ' col2'], dtype='object')
    >>> normalize_columns(df).columns
    Index(['COL1', 'COL2'], dtype='object')
    """
    df.columns = normalize_series(df.columns)
    return df


def normalize_dataframe(df: DataFrame) -> DataFrame:
    """Normalizes column names and values.

    Parameters
    ----------
    df : DataFrame
        DataFrame to be transformed.

    Returns
    -------
    DataFrame
        Transformed DataFrame.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'col1 ': ['Héllo', 'Wórld!'], ' col2': ['Foo!', 'Bar!']})
    >>> df
        col1  col2
    0  Héllo  Foo!
    1 Wórld!  Bar!
    >>> normalize_dataframe(df)
        COL1  COL2
    0  HELLO  FOO_
    1 WORLD_  BAR_
    """
    return normalize_columns(df).apply(normalize_series)


def usecols(columns: Sequence[str]) -> Callable[[str], bool]:
    """Returns a function that checks if a column name is in a list.

    Used in the ``usecols`` parameter of ``pandas.read_csv``
    and ``pandas.read_excel``.

    Parameters
    ----------
    columns : Sequence[str]
        List of column names.
    """

    def f(col: str) -> bool:
        return col.strip() in columns

    return f


def excel_reading_exc_middleware(
    exc: Exception, filename: str, sheet_name: str = ''
) -> Exception:
    """Middleware for known Excel files reading exceptions.

    If an error is known, return a custom message for that error.

    Parameters
    ----------
    exc : Exception
        The raised exception.
    filename : str
        The excel filename.
    sheet_name : str, optional
        The name of the sheet being read, if applicable, by default ''.

    Returns
    -------
    ExternalReadingError
        Excel file reading exception with a custom message.
    Exception
        If exception is not known.
    """
    sheet_name = sheet_name.strip()
    msg = str(exc)
    if msg.startswith('Worksheet') and msg.endswith('not found'):
        if not sheet_name:
            return ExternalReadingError(
                f'No se encontró la hoja predeterminada'
                f' en el archivo {filename!r}'
            )

        return ExternalReadingError(
            f'No se encontró la hoja {sheet_name!r}'
            f' en el archivo {filename!r}'
        )

    if isinstance(exc, KeyError):
        col_name = str(exc)
        if not sheet_name:
            return ExternalReadingError(
                f'No se encontró la columna {col_name}'
                f' en la hoja predeterminada'
                f' del archivo {filename!r}'
            )

        return ExternalReadingError(
            f'No se encontró la columna {col_name}'
            f' en la hoja {sheet_name!r}'
            f' del archivo {filename!r}'
        )

    return exc
