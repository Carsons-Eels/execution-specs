"""Shared gas repricing config loader and spec-side applier."""

import json
import os
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

_ENV_VAR = "EELS_GAS_REPRICING_CONFIG"


@lru_cache(maxsize=1)
def load_repricing_config() -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Load gas repricing overrides from JSON config.

    Return None if env var is unset or empty.
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

    warnings.warn(
        f"Gas repricing config loaded from {config_path}",
        stacklevel=2,
    )
    return config


def apply_spec_repricing(
    fork_name: str,
    gas_costs_class: type,
) -> None:
    """
    Apply repricing overrides to module globals.

    Mutates GasCosts in place, preserving the
    original type wrapper (Uint, U64, etc.).
    """
    config = load_repricing_config()
    if config is None:
        return

    overrides = config.get(fork_name)
    if overrides is None:
        return

    for name, value in overrides.items():
        if not hasattr(gas_costs_class, name):
            raise ValueError(
                f"Unknown gas constant '{fork_name}' "
                f"in repricing config for fork "
                f"'{name}'."
            )
        original = getattr(gas_costs_class, name)
        setattr(gas_costs_class, name, type(original)(value))
