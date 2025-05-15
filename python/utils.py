"""Utils."""


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

    """
    val = val.lower().strip()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    if val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    raise InvalidTruthValueError(val)
