import dataclasses
import inspect
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

from jsonmarshal.exceptions import UnmarshalError
from jsonmarshal.keys import get_json_key
from jsonmarshal.types import PRIMITIVES, TYPE_MAP, Type, get_optional_type, is_optional, is_typing, is_union

T = TypeVar("T")


# Special types that need further processing
# None is included here as it also needs custom handling.
CUSTOM_TYPES = {Type.NONETYPE, Type.UUID, Type.ENUM, Type.DATETIME, Type.DATE}


def unmarshal(
    response: Any, schema: T, datetime_fmt: Optional[str] = None, date_fmt: Optional[str] = None,
) -> T:
    unmarshaller = _Unmarshaller(response, schema, datetime_fmt, date_fmt)
    return unmarshaller.unmarshal()


@dataclasses.dataclass
class ResultContainer:
    data: Any
    schema: Any
    parent: str
    path: str
    parent_path: str
    cleaned: bool = False
    unmarshalled: bool = False
    _schema_type: Type = Type.NOT_SET

    @property
    def schema_type(self) -> Type:
        # Return the primitive python type for this item
        if self._schema_type is Type.NOT_SET:
            self._schema_type = get_type(self.schema, self.data)
        return self._schema_type

    @property
    def inner_schema(self) -> type:
        if is_union(self.schema):
            # If this is a union, we need to get the valid part of that union.
            schema = get_optional_type(self.schema)
        else:
            schema = self.schema

        return schema.__args__[0]

    @property
    def schema_fields(self) -> Dict[str, dataclasses.Field]:
        return self.schema.__dataclass_fields__

    @property
    def data_keys(self) -> List[str]:
        return list(self.data.keys())

    def validate_schema(self) -> None:
        # Validate that the stored data is of the expected type as specified by the user.
        if self.cleaned:
            return

        if self.schema_type in CUSTOM_TYPES:
            # Special types that don't get cleaned automatically
            return

        errmsg = (
            f"Invalid schema. schema = {self.schema}, data = '{self.data}' ({type(self.data)}) "
            f"at location = {self.parent}"
        )
        if TYPE_MAP[type(self.data)] != self.schema_type:
            raise UnmarshalError(errmsg)


class _Unmarshaller:
    def __init__(
        self, response: Any, schema: Any, datetime_fmt: Optional[str] = None, date_fmt: Optional[str] = None,
    ) -> None:
        self.result = [ResultContainer(data=response, schema=schema, parent="", parent_path="", path="")]
        self.datetime_fmt = datetime_fmt
        self.date_fmt = date_fmt
        self.dump: List[ResultContainer] = []
        self.processors: Dict[Any, Callable[[ResultContainer], None]] = {
            Type.LIST: self.process_list,
            Type.DICT: self.process_dict,
            Type.ENUM: self.process_enum,
            Type.UUID: self.process_uuid,
            Type.DATETIME: self.process_datetime,
            Type.DATE: self.process_date,
        }
        # Add each primitive individually
        for t in PRIMITIVES:
            self.processors[t] = self.process_primitive

    def unmarshal(self) -> Any:
        while self.result:
            item = self.get_item()

            if len(self.result) == 0 and item.cleaned and item.unmarshalled:
                # If this is the first item and it has already been cleaned
                # then we don't need to do anything
                continue

            processor = self.processors[item.schema_type]
            processor(item)

            self.promote()

        return item.data

    def get_item(self) -> ResultContainer:
        item = self.result.pop()
        item.validate_schema()
        return item

    def process_list(self, item: ResultContainer) -> None:
        if item.cleaned is False:
            item = self._clean_list(item)
        else:
            # If this is the second time we are seeing the list, it should already have all of its
            # children correctly marshalled and re-appended to it. So it should now be complete.
            item.unmarshalled = True

        # Put original (now empty item) back onto the result queue
        self.result.append(item)

    def _clean_list(self, item: ResultContainer) -> ResultContainer:
        index = 0
        while item.data:
            # Remove the element from the data (in order)
            elem = item.data.pop(0)
            self.dump.append(
                ResultContainer(
                    data=elem,
                    schema=item.inner_schema,
                    parent=item.parent,
                    parent_path=item.path,
                    path=f"{item.path}.{index}",
                )
            )
            index += 1

        item.cleaned = True
        return item

    def process_dict(self, item: ResultContainer) -> None:
        if not item.cleaned:
            # Go through each known field and fix the keys in the original dictionary
            item = self.clean_item(item)

        if not self.dump and item.unmarshalled is False:
            # This item has no children, we can safely unmarshal it to the specified datatype
            item.unmarshalled = True
            item.data = item.schema(**item.data)

        self.result.append(item)

    def clean_item(self, item: ResultContainer) -> ResultContainer:
        # Clean up the item (only called for dicts)
        for schema_key, field in item.schema_fields.items():
            json_key = self.get_json_key_for_item(field, item)

            if json_key not in item.data:
                # a check has already been performed to see if the json_key/schema_keys are valid
                # this means that it is an optional field that doesn't have data set correctly.
                item.data[schema_key] = None
                continue

            if json_key == schema_key:
                # No need to do anything, it's already named correctly
                continue

            v = item.data.pop(json_key)

            # Put the data back under the expected data key name
            item.data[schema_key] = v

        # Go through the data dict and remove any keys that are not defined in the data
        for data_key in item.data_keys:
            if data_key not in item.schema_fields:
                item.data.pop(data_key)

        for data_key, v in item.data.items():
            schema_type = item.schema.__annotations__[data_key]
            child = ResultContainer(
                data=v,
                schema=schema_type,
                parent=data_key,
                parent_path=item.path,
                path=f"{item.path}.{data_key}",
            )

            if child.schema_type not in PRIMITIVES:
                self.dump.append(child)
            else:
                # We want to validate that the primitives are actually using the specified data
                child.validate_schema()

        item.cleaned = True
        return item

    def process_primitive(self, item: ResultContainer) -> None:
        # Just need to set the cleaned flag for a primtive and put it back on the list
        item.cleaned = True
        item.unmarshalled = True
        self.result.append(item)

    def process_enum(self, item: ResultContainer) -> None:
        if is_union(item.schema):
            schema = get_optional_type(item.schema)
        else:
            schema = item.schema
        try:
            # Try to cast the data value into the specified enum type.
            v = schema(item.data)
        except ValueError:
            raise UnmarshalError(f"Unable to use data value '{item.data}' as Enum {item.schema}")

        item.data = v
        item.cleaned = True
        item.unmarshalled = True
        self.result.append(item)

    def process_uuid(self, item: ResultContainer) -> None:
        if is_union(item.schema):
            schema = get_optional_type(item.schema)
        else:
            schema = item.schema
        try:
            v = schema(item.data)
        except (ValueError, TypeError, AttributeError):
            raise UnmarshalError(f"Unable to use data value '{item.data}' as UUID {item.schema}")

        item.data = v
        item.cleaned = True
        item.unmarshalled = True
        self.result.append(item)

    def process_datetime(self, item: ResultContainer) -> None:
        data = item.data
        if self.datetime_fmt:
            # Prioritise the users specified time format.
            v = datetime.strptime(item.data, self.datetime_fmt)
        else:
            data = f"{data[:-1]}+00:00" if data.endswith("Z") else data
            v = datetime.fromisoformat(data)
        item.data = v
        item.cleaned = True
        item.unmarshalled = True
        self.result.append(item)

    def process_date(self, item: ResultContainer) -> None:
        if self.date_fmt:
            # Prioritise the users specified date format.
            v = datetime.strptime(item.data, self.date_fmt).date()
        else:
            v = date.fromisoformat(item.data)
        item.data = v
        item.cleaned = True
        item.unmarshalled = True
        self.result.append(item)

    def promote(self) -> None:
        # promote combines the last element with it's parents.

        if self.dump:
            # If the dump contains items, then there is still stuff to process
            self.flush_dump()
            return

        while len(self.result) >= 2:
            item = self.result.pop()
            prev = self.result.pop()

            if item.unmarshalled is False:
                # item is not ready to be promoted, move onto next one.
                self.dump.append(item)
                self.result.append(prev)
                continue

            # Check to see if the item can be attached to the previous key/array
            if item.parent_path != prev.path:
                # This item cannot be attached to the parent. see if it can be attached to the one after.
                self.result.append(item)
                self.dump.append(prev)
                continue

            if prev.schema_type == Type.LIST:
                prev.data.append(item.data)
                self.result.append(prev)
                continue

            if prev.schema_type == Type.DICT:
                # Put the object on the parents data key then back onto the result queue
                prev.data[item.parent] = item.data
                # prev has been updated so needs further processing
                self.result.append(prev)
                continue

        # Ensure that we haven't left anything in the dump
        self.flush_dump()

    def flush_dump(self) -> None:
        # Put all dumped items back onto the result queue
        while self.dump:
            self.result.append(self.dump.pop())

    @staticmethod
    def get_json_key_for_item(field: dataclasses.Field, item: ResultContainer) -> str:
        json_key = get_json_key(field)

        if json_key in item.data or is_field_optional(field):
            return json_key

        keys = list(item.data.keys()) if type(item.data) is dict else item.data
        raise UnmarshalError(
            f"Expected json key is not present in object at position '{item.path}'. "
            f"'{json_key}' not in {keys}"
        )


def is_field_optional(field: dataclasses.Field) -> bool:
    return is_optional(field.type)


def get_type(schema: Any, data: Any) -> Type:

    if dataclasses.is_dataclass(schema):
        return Type.DICT

    if inspect.isclass(schema) and issubclass(schema, Enum):
        return Type.ENUM

    if inspect.isclass(schema) and issubclass(schema, datetime):
        return Type.DATETIME

    if inspect.isclass(schema) and issubclass(schema, date):
        # Date check must come after datetime as datetime is a subclass of date
        return Type.DATE

    if is_union(schema):
        _validate_union_is_optional(schema)
        return _get_matching_union_type(schema, data)

    if is_typing(schema):
        # The data hasn't matched any previous check.
        # assuming it is a typing.* type which can be determined
        # from the __origin__ attribute
        schema = schema.__origin__

    if schema in TYPE_MAP:
        return TYPE_MAP[schema]

    raise UnmarshalError(f"Schema type '{schema}' is not currently supported.")


def _validate_union_is_optional(schema: Any) -> None:
    # Currently only supporting unions that denote Optional types.
    # Raising error if this is not the case
    if not is_optional(schema):
        raise UnmarshalError(
            "Schemas defined with unions containing anything other than optional (NoneType + other) "
            f"fields are not currently supported. Got {schema}  with  {schema.__args__}"
        )


def _get_matching_union_type(schema: None, data: None) -> Type:
    # Extract the expected type from the union.
    # As we only allow Optional types, we can safely extract the non-optional
    # type when the data is non-null
    if data is None:
        return Type.NONETYPE

    t = get_optional_type(schema)
    return get_type(t, data)
