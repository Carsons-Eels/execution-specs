"""Gas repricing override loader for fast iteration on gas schedules."""

import json
import os
import warnings
from dataclasses import fields, replace
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from .gas_costs import GasCosts

_ENV_VAR = "EELS_GAS_REPRICING_CONFIG"
_VALID_FIELDS = frozenset(f.name for f in fields(GasCosts))


@lru_cache(maxsize=1)
def load_repricing_config() -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Load gas repricing config from the path in EELS_GAS_REPRICING_CONFIG.

    Return None if env var is unset or empty.
    Raise FileNotFoundError if the file doesn't exist.
    Raise ValueError if any field name is not a valid GasCosts field.
    """
    config_path = os.environ.get(_ENV_VAR, "")
    if not config_path:
        return None

    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"{_ENV_VAR} points to non-existent file: {config_path}"
        )

    with open(path) as f:
        config = json.load(f)

    for fork_name, overrides in config.items():
        for field_name, value in overrides.items():
            if field_name not in _VALID_FIELDS:
                raise ValueError(
                    f"Unknown GasCosts field '{field_name}' "
                    f"in repricing config for fork '{fork_name}'. "
                    f"Valid fields: {sorted(_VALID_FIELDS)}"
                )
            if not isinstance(value, int):
                raise TypeError(
                    f"GasCosts field '{field_name}' for fork "
                    f"'{fork_name}' must be of type int, "
                    f"got {type(value).__name__}: {value!r}"
                )

    warnings.warn(
        f"Gas repricing config loaded from {config_path}",
        stacklevel=2,
    )
    return config


def apply_repricing(fork_name: str, base_costs: GasCosts) -> GasCosts:
    """Apply repricing overrides for fork_name to base_costs."""
    config = load_repricing_config()
    if config is None:
        return base_costs

    overrides = config.get(fork_name)
    if overrides is None:
        return base_costs

    return replace(base_costs, **overrides)
