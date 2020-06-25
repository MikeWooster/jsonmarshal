"""
Provide backwards compatibility for typing get_args/get_origin
"""
from typing import Any, Optional, Tuple


def _local_get_args(t: Any) -> Tuple[Any]:
    return t.__args__


def _local_get_origin(t: Any) -> Optional[Any]:
    if not _is_typing(t):
        return None
    return t.__origin__


def _is_typing(t: Any) -> bool:
    return hasattr(t, "__origin__")
