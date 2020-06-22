import dataclasses
import inspect
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from jsonmarshal.exceptions import UnmarshalError
from jsonmarshal.utils.typing import JsonType

T = TypeVar("T")

NoneType = type(None)

PRIMITIVES = {str, int, float, bool, NoneType}

# Special types that need further processing
# None is included here because
CUSTOM_TYPES = {NoneType, UUID, Enum, datetime, date}


def unmarshal(
    response: JsonType,
    schema: Generic[T],
    datetime_fmt: Optional[str] = None,
    date_fmt: Optional[str] = None,
) -> T:
    unmarshaller = _Unmarshaller(response, schema, datetime_fmt, date_fmt)
    return unmarshaller.unmarshal()


@dataclasses.dataclass
class ResultContainer:
    data: JsonType
    schema: Any
    parent: str
    path: str
    parent_path: str
    cleaned: bool = False
    unmarshalled: bool = False
    _schema_type: Optional[type] = None

    @property
    def schema_type(self) -> type:
        # Return the primitive python type for this item
        if self._schema_type is None:
            self._schema_type = self._calculate_schema_type(self.schema, self.data)
        return self._schema_type

    def _calculate_schema_type(self, schema, data) -> type:
        if schema in PRIMITIVES:
            calculated_type = schema

        elif dataclasses.is_dataclass(schema):
            calculated_type = dict

        elif schema is None:
            calculated_type = NoneType

        elif schema is UUID:
            calculated_type = UUID

        elif inspect.isclass(schema) and issubclass(schema, Enum):
            calculated_type = Enum

        elif inspect.isclass(schema) and issubclass(schema, datetime):
            calculated_type = datetime

        elif inspect.isclass(schema) and issubclass(schema, date):
            # Date check must come after datetime as datetime is a subclass of date
            calculated_type = date

        elif self._is_typing(schema) and self._is_union(schema):
            calculated_type = self._get_matching_union_type(schema, data)

        elif self._is_typing(schema):
            # The schema hasn't matched any previous check.
            # assuming it is a typing.* type which can be determined
            # from the __origin__ attribute
            calculated_type = schema.__origin__

        else:
            raise UnmarshalError(f"Schema type '{self.schema}' is not currently supported.")

        return calculated_type

    def _is_typing(self, schema) -> bool:
        return hasattr(schema, "__origin__")

    def is_union(self) -> bool:
        return self._is_typing(self.schema) and self._is_union(self.schema)

    def _is_union(self, schema) -> bool:
        # return if the schema is of a union type.
        if schema.__origin__ is not Union:
            return False

        # Currently only supporting unions that denote Optional types
        if len(schema.__args__) != 2 or NoneType not in schema.__args__:
            raise UnmarshalError(
                "Schemas defined with unions containing anything other than optional (NoneType + other) "
                f"fields are not currently supported. Got {schema}  with  {schema.__args__}"
            )
        return True

    def _get_matching_union_type(self, schema, data) -> type:
        # Extract the expected type from the union.
        # As we only allow Optional types, we can safely extract the non-optional
        # type when the data is non-null
        if data is None:
            return NoneType

        valid = [t for t in schema.__args__ if t is not NoneType]
        return self._calculate_schema_type(valid[0], data)

    def get_non_null_union_part(self) -> type:
        # Given a valid union; [NoneType, Float]
        # extract the non null part -> Float
        valid = [t for t in self.schema.__args__ if t is not NoneType]
        return valid[0]

    @property
    def inner_schema(self):
        if self.is_union():
            # If this is a union, we need to get the valid part of that union.
            schema = self.get_non_null_union_part()
        else:
            schema = self.schema

        return schema.__args__[0]

    @property
    def schema_fields(self):
        return self.schema.__dataclass_fields__

    @property
    def data_keys(self) -> List[str]:
        return list(self.data.keys())

    def validate_schema(self):
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
        if type(self.data) != self.schema_type:
            raise UnmarshalError(errmsg)


class _Unmarshaller:
    def __init__(
        self,
        response: JsonType,
        schema: Generic[T],
        datetime_fmt: Optional[str] = None,
        date_fmt: Optional[str] = None,
    ):
        self.result = [ResultContainer(data=response, schema=schema, parent="", parent_path="", path="")]
        self.datetime_fmt = datetime_fmt
        self.date_fmt = date_fmt
        self.dump = []
        self.processors: Dict[Any, Callable[[ResultContainer], None]] = {
            list: self.process_list,
            dict: self.process_dict,
            Enum: self.process_enum,
            UUID: self.process_uuid,
            datetime: self.process_datetime,
            date: self.process_date,
        }
        # Add each primitive individually
        for t in PRIMITIVES:
            self.processors[t] = self.process_primitive

    def unmarshal(self):
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

    def process_list(self, item: ResultContainer):
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

    def process_dict(self, item: ResultContainer):
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

            # Put the data back under the expected schema key name
            item.data[schema_key] = v

        # Go through the data dict and remove any keys that are not defined in the schema
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
                # We want to validate that the primitives are actually using the specified schema
                child.validate_schema()

        item.cleaned = True
        return item

    def process_primitive(self, item: ResultContainer):
        # Just need to set the cleaned flag for a primtive and put it back on the list
        item.cleaned = True
        item.unmarshalled = True
        self.result.append(item)

    def process_enum(self, item: ResultContainer):
        if item.is_union():
            schema = item.get_non_null_union_part()
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

    def process_uuid(self, item: ResultContainer):
        if item.is_union():
            schema = item.get_non_null_union_part()
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

    def process_datetime(self, item: ResultContainer):
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

    def process_date(self, item: ResultContainer):
        if self.date_fmt:
            # Prioritise the users specified date format.
            v = datetime.strptime(item.data, self.date_fmt).date()
        else:
            v = date.fromisoformat(item.data)
        item.data = v
        item.cleaned = True
        item.unmarshalled = True
        self.result.append(item)

    def promote(self):
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

            if prev.schema_type == list:
                prev.data.append(item.data)
                self.result.append(prev)
                continue

            if prev.schema_type == dict:
                # Put the object on the parents data key then back onto the result queue
                prev.data[item.parent] = item.data
                # prev has been updated so needs further processing
                self.result.append(prev)
                continue

        # Ensure that we haven't left anything in the dump
        self.flush_dump()

    def flush_dump(self):
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
    if field.type in PRIMITIVES:
        return False

    # The field is optional if it allows None values in it's union
    return type(None) in field.type.__args__


def get_json_key(field: dataclasses.Field) -> str:
    if field.metadata.get("json"):
        # The field is defined, we can just use this.
        return field.metadata["json"]

    return field.name
