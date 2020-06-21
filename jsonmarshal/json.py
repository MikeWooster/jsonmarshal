import dataclasses
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from jsonmarshal.utils.typing import JsonType

T = TypeVar("T")

NoneType = type(None)

PRIMITIVES = {str, int, float, NoneType}



def unmarshal_response(schema: Generic[T]):
    """Decorator to unmarshal the response into the provided dataclass."""

    def decorator(func) -> T:
        def wrap(*args, **kwargs) -> T:
            response = func(*args, **kwargs)
            return unmarshal(response, schema)

        return wrap

    return decorator


class UnmarshalError(Exception):
    pass


class SchemaStart:
    pass


class SchemaEnd:
    pass


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
        return self.schema.__origin__

    @property
    def item_type(self):
        return type(self.data)

    @property
    def inner_schema(self):
        return self.schema.__args__[0]

    @property
    def schema_fields(self):
        return self.schema.__dataclass_fields__

    @property
    def data_keys(self) -> List[str]:
        return list(self.data.keys())


class _Unmarshaller:
    def __init__(self, response, schema):
        self.result = [ResultContainer(data=response, schema=schema, parent=None)]
        self.dump = []
        self.processors: Dict[Any, Callable[[ResultContainer], None]] = {
            list: self.process_list,
            dict: self.process_dict,
        }
        # Add each primitive individually
        for t in PRIMITIVES:
            self.processors[t] = self.process_primitive

    def unmarshal(self):
        while self.result:
            item = self.get_item()

            if len(self.result) == 0 and item.cleaned and item.unmarshalled:
                # If this is the first item and it has already been cleaned then we don't need to do anything
                continue

            processor = self.processors[item.item_type]
            processor(item)

            self.promote()

        return item.data

    def get_item(self) -> ResultContainer:
        item = self.result.pop()
        self.validate_schema(item)
        return item

    @staticmethod
    def validate_schema(item: ResultContainer):
        if item.cleaned:
            return
        if item.schema_type is NoneType:
            return

        errmsg = "Invalid schema. schema = {schema}, data = {data}".format(
            schema=item.schema_type, data=item.item_type
        )

        if item.schema_type is Union:
            if dict in item.schema.__args__ or list in item.schema.__args__:
                # including dict/list in a union type in a schema is invalid.
                raise UnmarshalError(
                    "{prefix}. Unions cannot contain dict or list items in a schema.".format(prefix=errmsg)
                )

            if item.item_type not in item.schema.__args__:
                raise UnmarshalError(errmsg)
        elif item.item_type != item.schema_type:
            raise UnmarshalError(errmsg)

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

        if not self.dump:
            # This item has no children, we can safely unmarshal it to the specified datatype
            item.unmarshalled = True
            item.data = item.schema(**item.data)

        item.cleaned = True
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
            if type(v) not in PRIMITIVES:
                self.dump.append(child)
            else:
                # We want to validate that the primatives are actually using the specified schema
                self.validate_schema(child)

        return item

    def process_primitive(self, item: ResultContainer):
        # Just need to set the cleaned flag for a primtive and put it back on the list
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

    if field.type.__origin__ is not Union:
        return False

    # The field is optional if it allows None values in it's union
    return type(None) in field.type.__args__


def get_json_key(field: dataclasses.Field) -> str:
    if field.metadata.get("json"):
        # The field is defined, we can just use this.
        return field.metadata["json"]

    return field.name