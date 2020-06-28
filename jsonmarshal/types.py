from datetime import date, datetime
from enum import Enum
from typing import Any, Union
from uuid import UUID

try:
    from typing import get_args, get_origin  # type: ignore
except ImportError:  # pragma: no cover
    # get_args/get_origin only available in py 3.8+
    from jsonmarshal.utils.typing import _local_get_origin as get_origin  # type: ignore
    from jsonmarshal.utils.typing import _local_get_args as get_args  # type: ignore


JsonType = Union[str, int, float, dict, list]
NoneType = type(None)


class _Type(Enum):
    """Enum of types."""

    NOT_SET = "NOT_SET"
    DATACLASS = "DATACLASS"
    NONETYPE = "NONETYPE"
    LIST = "LIST"
    DICT = "DICT"
    STRING = "STRING"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    UUID = "UUID"
    ENUM = "ENUM"
    DATETIME = "DATETIME"
    DATE = "DATE"


_TYPE_MAP = {
    None: _Type.NONETYPE,
    NoneType: _Type.NONETYPE,
    str: _Type.STRING,
    int: _Type.INT,
    float: _Type.FLOAT,
    bool: _Type.BOOL,
    datetime: _Type.DATETIME,
    date: _Type.DATE,
    UUID: _Type.UUID,
    dict: _Type.DICT,
    list: _Type.LIST,
}

_PRIMITIVES = {_Type.STRING, _Type.INT, _Type.FLOAT, _Type.BOOL, _Type.NONETYPE}


def _is_optional(t: Any) -> bool:
    """Determine if this type is a defined Optional[...] type."""
    if not _is_union(t):
        return False

    args = get_args(t)
    if len(args) != 2 or NoneType not in args:
        return False

    return True


def _is_union(t: Any) -> bool:
    """Determine if this type is defined as a Union[...] type."""
    return get_origin(t) is Union


def _get_optional_type(t: Any) -> Any:
    """Given a Optional type, return the type that is non-null"""
    valid = [t for t in get_args(t) if t is not NoneType]
    return valid[0]


def _is_typing(t: Any) -> bool:
    """Determine if the type `t` is of `typing` origin."""
    return get_origin(t) is not None
