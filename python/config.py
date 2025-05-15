"""Configuration."""

import dataclasses
import os
from collections.abc import Mapping

from dotenv import load_dotenv

from .utils import strtobool  # TODO: Implement this function


class EnforcedDataclassMixin:
    """Enforces types at runtime."""

    def __post_init__(self) -> None:
        """Enforces types at runtime.

        This is necessary because `dataclasses` does not enforce types at runtime,
        and we want to be able to pass the environment variables as strings.

        Raises
        ------
        ValueError
            If the value cannot be converted to the field type.

        """
        for field in dataclasses.fields(self):  # type: ignore
            value = getattr(self, field.name)
            if field.type is bool and isinstance(value, str):
                value = strtobool(value)
            if field.type is list and isinstance(value, str):
                value = [v.strip() for v in value.split(',')]
            setattr(self, field.name, field.type(value))  # type: ignore


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
