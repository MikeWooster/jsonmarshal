import dataclasses
from typing import Any, Union

from jsonmarshal.types import _is_optional


def json_field(
    *args: list, json: str = None, omitempty: bool = False, metadata: dict = None, **kwargs: dict
) -> dataclasses.Field:
    """Extend the python dataclass field with additional arguments.

    The "json" option specifies the string key to be used when
    marshalling/unmarshalling to/from json. When the "json" option
    is not specified, the key on the dataclass will be used.

    The "omitempty" option specifies that the field should be omitted
    from marshalling if the field is typed as an `Optional[...]` value,
    and is set to `None`.

    E.g. A dataclass defining the field results in the following json:
     - `my_value: str`  ->  {"my_value": ...}.
     - `my_value: str = json_field(json="myValue")`  ->  {"myValue": ...}
     - `my_value: Optional[str] = json_field(omitempty=True)`  ->  {} (when my_value = None)
    """
    if metadata is None:
        metadata = {}

    metadata["json"] = json
    metadata["omitempty"] = omitempty

    return dataclasses.field(*args, metadata=metadata, **kwargs)  # type: ignore


def _get_json_key(field: dataclasses.Field) -> str:
    """Given a json field, extract the key."""
    if field.metadata.get("json"):
        # The field is defined, we can just use this.
        return field.metadata["json"]

    return field.name


def _omit_field(field: dataclasses.Field, value: Union[None, Any]) -> bool:
    """Can the field be omitted when marshalling?"""
    omit = field.metadata.get("omitempty", False)
    if omit and value is None and _is_optional(field.type):
        return True
    return False
