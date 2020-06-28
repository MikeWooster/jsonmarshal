import dataclasses
import inspect
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

from jsonmarshal.exceptions import MarshalError
from jsonmarshal.fields import _get_json_key, _omit_field
from jsonmarshal.types import _PRIMITIVES, _TYPE_MAP, _Type

T = TypeVar("T")


def marshal(data: Any, datetime_fmt: Optional[str] = None, date_fmt: Optional[str] = None) -> Any:
    """Marshal python dataclasses into json.

    Given a dataclass `X`, marshal it into a json serializable format.

    The "datetime_fmt" option allows the user to specify the format to
    use when marshalling a datetime object into a string.

    The "date_fmt" option allows the user to specify the format to use
    when marshalling a date object into a string.

    Both "datetime_fmt" and "date_fmt" options use the strftime/strptime behaviour:
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    marshaller = _Marshaller(data, datetime_fmt, date_fmt)
    return marshaller.marshal()


@dataclasses.dataclass
class _ResultContainer:
    data: Any
    parent_key: str
    path: str
    parent_path: str
    cleaned: bool = False
    marshalled: bool = False
    _schema_type: _Type = _Type.NOT_SET

    @property
    def schema_type(self) -> _Type:
        # Return the primitive python type for this item
        if self._schema_type is _Type.NOT_SET:
            self._schema_type = _get_type(self.data)
        return self._schema_type


class _Marshaller:
    def __init__(
        self, result: Any, datetime_fmt: Optional[str] = None, date_fmt: Optional[str] = None,
    ) -> None:
        self.result = [_ResultContainer(data=result, parent_key="", parent_path="", path="")]
        self.datetime_fmt = datetime_fmt
        self.date_fmt = date_fmt
        self.dump: List[_ResultContainer] = []
        self.processors: Dict[_Type, Callable[[_ResultContainer], None]] = {
            _Type.DATACLASS: self.process_dataclass,
            _Type.LIST: self.process_list,
            _Type.DICT: self.process_dict,
            _Type.ENUM: self.process_enum,
            _Type.UUID: self.process_uuid,
            _Type.DATETIME: self.process_datetime,
            _Type.DATE: self.process_date,
        }
        # Add each primitive individually
        for t in _PRIMITIVES:
            self.processors[t] = self.process_primitive

    def marshal(self) -> T:
        while self.result:
            item = self.get_item()
            if len(self.result) == 0 and item.cleaned and item.marshalled:
                # If this is the first item and it has already been cleaned
                # then we don't need to do anything
                continue

            processor = self.processors[item.schema_type]
            processor(item)

            self.promote()

        return item.data

    def get_item(self) -> _ResultContainer:
        item = self.result.pop()
        return item

    def process_dataclass(self, item: _ResultContainer) -> None:
        # Input type is dataclass, extract fields and create dict
        if not item.cleaned:
            item = self.clean_dataclass(item)

        if not self.dump and item.marshalled is False:
            # No values need further marshalling, therefore this item is done.
            item.marshalled = True

        self.result.append(item)

    def clean_dataclass(self, item: _ResultContainer) -> _ResultContainer:
        marshalled = {}

        for field in item.data.__dataclass_fields__.values():
            json_key = _get_json_key(field)
            value = item.data.__dict__[field.name]

            # As this is a dataclass, we are relying on the fact that python
            # will only allow certain types to be set on it, so we just figure out
            # the type of the underlying value here.
            type_ = _get_type(value)

            if _omit_field(field, value):
                continue

            if type_ in _PRIMITIVES:
                # Primitive values can be attached directly to the new dict
                marshalled[json_key] = value
            else:
                # value needs further marshalling. add to dump for later processing.
                r = _ResultContainer(
                    data=value, parent_key=json_key, parent_path=item.path, path=f"{item.path}.{json_key}",
                )
                self.dump.append(r)

        item.data = marshalled
        item.cleaned = True

        return item

    def process_list(self, item: _ResultContainer) -> None:
        if item.cleaned is False:
            item = self._clean_list(item)
        else:
            item.marshalled = True

        self.result.append(item)

    def _clean_list(self, item: _ResultContainer) -> _ResultContainer:
        index = 0

        while item.data:
            # Remove element from the data in order
            elem = item.data.pop(0)

            r = _ResultContainer(
                data=elem, parent_key=item.parent_key, parent_path=item.path, path=f"{item.path}.{index}"
            )
            self.dump.append(r)
            index += 1

        item.cleaned = True
        return item

    def process_dict(self, item: _ResultContainer) -> None:
        # Assume a dict is already properly structured and ok for marshalling
        item.cleaned = True
        item.marshalled = True
        self.result.append(item)

    def process_primitive(self, item: _ResultContainer) -> None:
        item.cleaned = True
        item.marshalled = True
        self.result.append(item)

    def process_datetime(self, item: _ResultContainer) -> None:
        if self.datetime_fmt:
            item.data = item.data.strftime(self.datetime_fmt)
        else:
            item.data = item.data.isoformat()
        item.cleaned = True
        item.marshalled = True
        self.result.append(item)

    def process_date(self, item: _ResultContainer) -> None:
        if self.date_fmt:
            item.data = item.data.strftime(self.date_fmt)
        else:
            item.data = item.data.isoformat()
        item.cleaned = True
        item.marshalled = True
        self.result.append(item)

    def process_enum(self, item: _ResultContainer) -> None:
        item.data = item.data.value
        item.cleaned = True
        item.marshalled = True
        self.result.append(item)

    def process_uuid(self, item: _ResultContainer) -> None:
        item.data = str(item.data)
        item.cleaned = True
        item.marshalled = True
        self.result.append(item)

    def promote(self) -> None:

        if self.dump:
            # If the dump contains items, then there is still stuff to process
            self.flush_dump()
            return

        while len(self.result) >= 2:
            item = self.result.pop()
            prev = self.result.pop()

            if item.marshalled is False:
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

            if prev.schema_type == _Type.LIST:
                prev.data.append(item.data)
                self.result.append(prev)
                continue

            if prev.schema_type == _Type.DATACLASS:
                # Put the object on the parents data key then back onto the result queue
                prev.data[item.parent_key] = item.data
                # prev has been updated so needs further processing
                self.result.append(prev)
                continue

            # The following exception has been included as a failsafe.
            # It is not expected for the program to get here, but that
            # doesn't mean it's impossible.
            raise MarshalError(
                "Unexpected Error occurred. Please file an issue with the repo to address this."
            )  # pragma: no cover

        # Ensure that we haven't left anything in the dump
        self.flush_dump()

    def flush_dump(self) -> None:
        # Put all dumped items back onto the result queue
        while self.dump:
            self.result.append(self.dump.pop())


def _get_type(data: Any) -> _Type:
    if dataclasses.is_dataclass(data):
        return _Type.DATACLASS

    type_of_data = type(data)

    if type_of_data is list:
        return _Type.LIST

    if type_of_data is dict:
        return _Type.DICT
        # raise MarshalError(f"Marshalling to json is not supported for dicts: {data}")

    if type_of_data in _TYPE_MAP:
        return _TYPE_MAP[type_of_data]

    if not inspect.isclass(data) and isinstance(data, Enum):
        return _Type.ENUM

    raise MarshalError(f"Unable to marshal data '{data}' ({type_of_data}) to known type.")
