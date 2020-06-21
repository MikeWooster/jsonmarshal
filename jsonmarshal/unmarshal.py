import dataclasses
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from jsonmarshal.exceptions import UnmarshalError
from jsonmarshal.utils.typing import JsonType

T = TypeVar("T")

NoneType = type(None)

PRIMITIVES = {str, int, float, NoneType}


def unmarshal(response: JsonType, schema: Generic[T]) -> T:
    unmarshaller = _Unmarshaller(response, schema)
    return unmarshaller.unmarshal()


@dataclasses.dataclass
class ResultContainer:
    data: JsonType
    schema: Any
    parent: Optional[str]
    cleaned: bool = False
    unmarshalled: bool = False

    @property
    def schema_type(self):
        # Return the primitive python type
        if self.schema in PRIMITIVES:
            return self.schema

        if dataclasses.is_dataclass(self.schema):
            return dict

        if self.schema is None:
            return NoneType

        try:
            if issubclass(self.schema, Enum):
                return Enum
        except TypeError:
            # Cant check for subclasses when self.schema is not a class
            pass

        # The schema hasn't matched any previous check.
        # assuming it is a typing.* type which can be determined
        # from the __origin__ attribute
        try:
            return self.schema.__origin__
        except AttributeError:
            raise UnmarshalError(f"Schema type '{self.schema}' is not currently supported.")

    @property
    def item_type(self):
        if self.schema_type is Union:
            # We have to use the type of the data itself
            # and rely upon another method validating the union is correct
            return type(self.data)
        # We assume that the schema has been defined correctly, and use that type
        return self.schema_type

    @property
    def inner_schema(self):
        return self.schema.__args__[0]

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

        if self.schema_type in [NoneType, Enum]:
            # Special types that don't get cleaned automatically
            return

        errmsg = "Invalid schema. schema = {schema}, data = {data}".format(
            schema=self.schema, data=type(self.data)
        )

        if self.schema_type is Union:
            if dict in self.schema.__args__ or list in self.schema.__args__:
                # including dict/list in a union type in a schema is invalid.
                raise UnmarshalError(
                    "{prefix}. Unions cannot contain dict or list items in a schema.".format(prefix=errmsg)
                )

            if self.item_type not in self.schema.__args__:
                raise UnmarshalError(errmsg)

        elif type(self.data) != self.schema_type:
            raise UnmarshalError(errmsg)


class _Unmarshaller:
    def __init__(self, response, schema):
        self.result = [ResultContainer(data=response, schema=schema, parent=None)]
        self.dump = []
        self.processors: Dict[Any, Callable[[ResultContainer], None]] = {
            list: self.process_list,
            dict: self.process_dict,
            Enum: self.process_enum,
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

            processor = self.processors[item.item_type]
            processor(item)

            self.promote()

        return item.data

    def get_item(self) -> ResultContainer:
        item = self.result.pop()
        item.validate_schema()
        return item

    def process_list(self, item: ResultContainer):
        # Need to append to an intermediary list in order to preserve the final list order.
        rev = []
        while item.data:
            elem = item.data.pop()
            rev.append(ResultContainer(data=elem, schema=item.inner_schema, parent=item.parent))
        while rev:
            self.dump.append(rev.pop())

        # Put original (now empty item) back onto the result queue
        item.cleaned = True
        item.unmarshalled = True
        self.result.append(item)

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
            child = ResultContainer(data=v, schema=schema_type, parent=data_key)

            if child.item_type not in PRIMITIVES:
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
        try:
            # Try to cast the data value into the specified enum type.
            v = item.schema(item.data)
        except ValueError:
            raise UnmarshalError(f"Unable to use data value '{item.data}' as Enum {item.schema}")

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

            if item.cleaned is False:
                # This can happen when dealing with list of objects. we still need to unmarshall this data
                # putting both back on the result queue for processing and ending the promotion stage
                self.result.append(prev)
                self.result.append(item)
                break

            if prev.cleaned is False:
                # Previous item still needs processing
                self.dump.append(prev)
                self.result.append(item)
                continue

            if prev.schema_type == list:
                # At this point item should be fully unmarshalled so appending directly
                # to the prev list will be possible
                if item.schema_type is dict and item.unmarshalled is False:
                    # any unmarshalled dictionaries will need unmarshalling
                    # at this point before appending to the list
                    item.data = item.schema(**item.data)
                    item.unmarshalled = True

                prev.data.append(item.data)
                self.result.append(prev)
                self.flush_dump()

            elif prev.schema_type == dict and item.parent in prev.data:
                # Put the object on the parents data key then back onto the result queue
                prev.data[item.parent] = item.data
                # prev has been updated so needs further processing
                self.result.append(prev)

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

        raise UnmarshalError(
            "Expected json key is not present in object. {key} not in {data}".format(
                key=json_key, data=item.data
            )
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
