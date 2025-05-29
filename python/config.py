"""Configuration."""

import dataclasses
simport os
from collections.abc import Mapping
from types import UnionType
from typing import Literal, Union, get_args, get_origin

from dotenv import load_dotenv


def strtobool(val: str) -> Literal[0, 1]:
    """Converts a string representation of truth to
    true (1) or false (0).

    True values are ``y``, ``yes``, ``t``, ``true``, ``on``, and ``1``;
    false values are ``n``, ``no``, ``f``, ``false``, ``off``, and ``0``.

    Raises
    ------
    ValueError
        If ``'val`` is anything else.

    Examples
    --------
    >>> strtobool('YES')
    1
    >>> strtobool('yes')
    1
    >>> strtobool('no')
    0
    >>> strtobool('1')
    1
    >>> strtobool('0')
    0
    >>> strtobool('true')
    1
    >>> strtobool('false')
    0
    """
    val = val.lower().strip()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError(f'invalid truth value {val!r}')


class EnforcedDataclassMixin:
    def __post_init__(self):
        """Enforces types at runtime."""
        for field in dataclasses.fields(self):  # type: ignore
            value = getattr(self, field.name)
            if value is None:
                setattr(self, field.name, value)
                continue

            if field.type is bool and isinstance(value, str):
                value = strtobool(value)
            if field.type is list and isinstance(value, str):
                value = [v.strip() for v in value.split(',')]
            if self._is_union(field.type):
                field.type = self._get_actual_type(field.type, value)

            setattr(self, field.name, field.type(value))  # type: ignore

    def _is_union(self, t: object) -> bool:
        origin = get_origin(t)
        return origin is Union or origin is UnionType

    def _get_actual_type(self, t: object, value: object):
        for type_ in get_args(t):
            if isinstance(value, type_):
                return type_


@dataclasses.dataclass
class EnvironmentVariables(EnforcedDataclassMixin):
    """Environment variables."""

    PROD: bool
    PORT: int


def get_config_from_map(env_map: Mapping) -> EnvironmentVariables:
    """Get the config from an environment map.

    Parameters
    ----------
    env_map : Mapping
        Environment map, for example, `os.environ`.

    Returns
    -------
    EnvironmentVariables
        Config.

    """
    field_names = [field.name for field in dataclasses.fields(EnvironmentVariables)]
    env_vars = {key: value for key, value in env_map.items() if key in field_names}
    return EnvironmentVariables(**env_vars)


load_dotenv()
config = get_config_from_map(os.environ)
