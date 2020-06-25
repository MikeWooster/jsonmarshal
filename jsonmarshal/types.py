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


class Type(Enum):
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


TYPE_MAP = {
    None: Type.NONETYPE,
    NoneType: Type.NONETYPE,
    str: Type.STRING,
    int: Type.INT,
    float: Type.FLOAT,
    bool: Type.BOOL,
    datetime: Type.DATETIME,
    date: Type.DATE,
    UUID: Type.UUID,
    dict: Type.DICT,
    list: Type.LIST,
}

PRIMITIVES = {Type.STRING, Type.INT, Type.FLOAT, Type.BOOL, Type.NONETYPE}


def is_optional(t: Any) -> bool:
    """Determine if this type is a defined Optional[...] type."""
    if not is_union(t):
        return False

    args = get_args(t)
    if len(args) != 2 or NoneType not in args:
        return False

    return True


def is_union(t: Any) -> bool:
    """Determine if this type is defined as a Union[...] type."""
    return get_origin(t) is Union


def get_optional_type(t: Any) -> Any:
    """Given a Optional type, return the type that is non-null"""
    valid = [t for t in get_args(t) if t is not NoneType]
    return valid[0]


def is_typing(t: Any) -> bool:
    """Determine if the type `t` is of `typing` origin."""
    return get_origin(t) is not None
