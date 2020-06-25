import enum
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Union
from uuid import UUID

import pytest
import pytz

from jsonmarshal.exceptions import UnmarshalError
from jsonmarshal.fields import json_field
from jsonmarshal.unmarshal import unmarshal
from tests.fixtures import load_fixtures


@pytest.mark.parametrize(
    "fixture_name,marshalled,schema,unmarshalled,date_fmt,datetime_fmt", load_fixtures()
)
def test_unmarshal_integration(fixture_name, marshalled, schema, unmarshalled, date_fmt, datetime_fmt):
    got = unmarshal(marshalled, schema, date_fmt=date_fmt, datetime_fmt=datetime_fmt)
    assert got == unmarshalled


def test_unmarshal_complex():
    # Test that tries to combine all the usable types into one test.
    # exercises the complexity of the unmarshalling.
    class Size(enum.Enum):
        SMALL = "SMALL"
        MEDIUM = "MEDIUM"
        LARGE = "LARGE"

    @dataclass
    class Item:
        int_key: int = json_field(json="intKey")
        float_key: float = json_field(json="floatKey")
        str_key: str = json_field(json="strKey")
        datetime_key: datetime = json_field(json="datetimeKey")
        date_key: date = json_field(json="dateKey")
        enum_key: Size = json_field(json="enumKey")

        optional_valid_int_key: Optional[int] = json_field(json="optionalValidIntKey")
        optional_valid_float_key: Optional[float] = json_field(json="optionalValidFloatKey")
        optional_valid_str_key: Optional[str] = json_field(json="optionalValidStrKey")
        optional_valid_datetime_key: Optional[datetime] = json_field(json="optionalValidDatetimeKey")
        optional_valid_date_key: Optional[date] = json_field(json="optionalValidDateKey")
        optional_valid_enum_key: Optional[Size] = json_field(json="optionalValidEnumKey")

        optional_null_int_key: Optional[int] = json_field(json="optionalNullIntKey")
        optional_null_float_key: Optional[float] = json_field(json="optionalNullFloatKey")
        optional_null_str_key: Optional[str] = json_field(json="optionalNullStrKey")
        optional_null_datetime_key: Optional[datetime] = json_field(json="optionalNullDatetimeKey")
        optional_null_date_key: Optional[date] = json_field(json="optionalNullDateKey")
        optional_null_enum_key: Optional[Size] = json_field(json="optionalNullEnumKey")

    @dataclass
    class Response(Item):
        important_item: Item = json_field(json="importantItem")

        items_list: List[Item] = json_field(json="itemsList")

        int_list: List[int] = json_field(json="intList")
        float_list: List[float] = json_field(json="floatList")
        str_list: List[str] = json_field(json="strList")
        datetime_list: List[datetime] = json_field(json="datetimeList")
        date_list: List[date] = json_field(json="dateList")
        enum_list: List[Size] = json_field(json="enumList")

        # Include the complete item here too
        int_key: int = json_field(json="intKey")
        float_key: float = json_field(json="floatKey")
        str_key: str = json_field(json="strKey")
        datetime_key: datetime = json_field(json="datetimeKey")
        date_key: date = json_field(json="dateKey")
        enum_key: Size = json_field(json="enumKey")

        optional_valid_int_key: Optional[int] = json_field(json="optionalValidIntKey")
        optional_valid_float_key: Optional[float] = json_field(json="optionalValidFloatKey")
        optional_valid_str_key: Optional[str] = json_field(json="optionalValidStrKey")
        optional_valid_datetime_key: Optional[datetime] = json_field(json="optionalValidDatetimeKey")
        optional_valid_date_key: Optional[date] = json_field(json="optionalValidDateKey")
        optional_valid_enum_key: Optional[Size] = json_field(json="optionalValidEnumKey")

        optional_null_int_key: Optional[int] = json_field(json="optionalNullIntKey")
        optional_null_float_key: Optional[float] = json_field(json="optionalNullFloatKey")
        optional_null_str_key: Optional[str] = json_field(json="optionalNullStrKey")
        optional_null_datetime_key: Optional[datetime] = json_field(json="optionalNullDatetimeKey")
        optional_null_date_key: Optional[date] = json_field(json="optionalNullDateKey")
        optional_null_enum_key: Optional[Size] = json_field(json="optionalNullEnumKey")

    item = {
        "intKey": 100,
        "floatKey": 100.99,
        "strKey": "string-key-value",
        "datetimeKey": "2020-06-22T10:07:30+00:00",
        "dateKey": "2020-06-22",
        "enumKey": "MEDIUM",
        "optionalValidIntKey": 100,
        "optionalValidFloatKey": 100.99,
        "optionalValidStrKey": "string-key-value",
        "optionalValidDatetimeKey": "2020-06-22T10:07:30+00:00",
        "optionalValidDateKey": "2020-06-22",
        "optionalValidEnumKey": "MEDIUM",
        "optionalNullIntKey": None,
        "optionalNullFloatKey": None,
        "optionalNullStrKey": None,
        "optionalNullDatetimeKey": None,
        "optionalNullDateKey": None,
        "optionalNullEnumKey": None,
    }
    json = {
        "importantItem": {**item},
        "itemsList": [{**item}, {**item}, {**item}],
        "intList": [1, 2, 3],
        "floatList": [1.99, 2.99, 3.99],
        "strList": ["val1", "val2", "val3"],
        "datetimeList": [
            "2020-06-22T10:07:30+00:00",
            "2020-06-23T10:07:30+00:00",
            "2020-06-24T10:07:30+00:00",
        ],
        "dateList": ["2020-06-22", "2020-06-23", "2020-06-24"],
        "enumList": ["SMALL", "MEDIUM", "LARGE"],
        **item,
    }

    want_item = Item(
        int_key=100,
        float_key=100.99,
        str_key="string-key-value",
        datetime_key=datetime(2020, 6, 22, 10, 7, 30, tzinfo=pytz.UTC),
        date_key=date(2020, 6, 22),
        enum_key=Size.MEDIUM,
        optional_valid_int_key=100,
        optional_valid_float_key=100.99,
        optional_valid_str_key="string-key-value",
        optional_valid_datetime_key=datetime(2020, 6, 22, 10, 7, 30, tzinfo=pytz.UTC),
        optional_valid_date_key=date(2020, 6, 22),
        optional_valid_enum_key=Size.MEDIUM,
        optional_null_int_key=None,
        optional_null_float_key=None,
        optional_null_str_key=None,
        optional_null_datetime_key=None,
        optional_null_date_key=None,
        optional_null_enum_key=None,
    )
    want = Response(
        important_item=want_item,
        items_list=[want_item, want_item, want_item],
        int_list=[1, 2, 3],
        float_list=[1.99, 2.99, 3.99],
        str_list=["val1", "val2", "val3"],
        datetime_list=[
            datetime(2020, 6, 22, 10, 7, 30, tzinfo=pytz.UTC),
            datetime(2020, 6, 23, 10, 7, 30, tzinfo=pytz.UTC),
            datetime(2020, 6, 24, 10, 7, 30, tzinfo=pytz.UTC),
        ],
        date_list=[date(2020, 6, 22), date(2020, 6, 23), date(2020, 6, 24)],
        enum_list=[Size.SMALL, Size.MEDIUM, Size.LARGE],
        int_key=100,
        float_key=100.99,
        str_key="string-key-value",
        datetime_key=datetime(2020, 6, 22, 10, 7, 30, tzinfo=pytz.UTC),
        date_key=date(2020, 6, 22),
        enum_key=Size.MEDIUM,
        optional_valid_int_key=100,
        optional_valid_float_key=100.99,
        optional_valid_str_key="string-key-value",
        optional_valid_datetime_key=datetime(2020, 6, 22, 10, 7, 30, tzinfo=pytz.UTC),
        optional_valid_date_key=date(2020, 6, 22),
        optional_valid_enum_key=Size.MEDIUM,
        optional_null_int_key=None,
        optional_null_float_key=None,
        optional_null_str_key=None,
        optional_null_datetime_key=None,
        optional_null_date_key=None,
        optional_null_enum_key=None,
    )
    got = unmarshal(json, Response)
    assert got == want


def test_iterable_json_with_optional_fields():
    @dataclass
    class Item:
        first_val: str = json_field(json="firstVal")
        second_val: int = json_field(json="secondVal")
        third_val: float = json_field(json="thirdVal")
        fourth_val: Optional[str] = json_field(json="fourthVal")

    json = [
        {"firstVal": "foo", "secondVal": 123, "thirdVal": 456.789, "fourthVal": None},
        {"firstVal": "bar", "secondVal": 654, "thirdVal": 555.241, "fourthVal": "pong"},
        {"firstVal": "baz", "secondVal": 987, "thirdVal": 111.324, "fourthVal": None},
    ]

    want = [
        Item(first_val="foo", second_val=123, third_val=456.789, fourth_val=None),
        Item(first_val="bar", second_val=654, third_val=555.241, fourth_val="pong"),
        Item(first_val="baz", second_val=987, third_val=111.324, fourth_val=None),
    ]

    got = unmarshal(json, List[Item])
    assert got == want


def test_iterable_json_no_optional_fields():
    @dataclass
    class Item:
        first_val: str = json_field(json="firstVal")
        second_val: int = json_field(json="secondVal")
        third_val: float = json_field(json="thirdVal")
        fourth_val: str = json_field(json="fourthVal")

    json = [
        {"firstVal": "foo", "secondVal": 123, "thirdVal": 456.789, "fourthVal": "4ping"},
        {"firstVal": "bar", "secondVal": 654, "thirdVal": 555.241, "fourthVal": "pong"},
        {"firstVal": "baz", "secondVal": 987, "thirdVal": 111.324, "fourthVal": "8num"},
    ]

    want = [
        Item(first_val="foo", second_val=123, third_val=456.789, fourth_val="4ping"),
        Item(first_val="bar", second_val=654, third_val=555.241, fourth_val="pong"),
        Item(first_val="baz", second_val=987, third_val=111.324, fourth_val="8num"),
    ]

    got = unmarshal(json, List[Item])
    assert got == want


def test_simple_object():
    @dataclass
    class Item:
        first_val: str = json_field(json="firstVal")

    json = {"firstVal": "hello"}

    want = Item(first_val="hello")
    got = unmarshal(json, Item)
    assert got == want


def test_simple_object_with_fields_we_dont_care_about():
    @dataclass
    class Item:
        first_val: str = json_field(json="firstVal")

    json = {"firstVal": "hello", "secondVal": "there"}

    want = Item(first_val="hello")
    got = unmarshal(json, Item)
    assert got == want


def test_simple_array():
    json = ["elem1", "elem2", "elem3"]

    got = unmarshal(json, List[str])
    want = json
    assert got == want


def test_simple_array_with_simple_object():
    @dataclass
    class Item:
        first_val: str = json_field(json="firstVal")

    json = [{"firstVal": "hello", "secondVal": "there"}]

    want = [Item(first_val="hello")]
    got = unmarshal(json, List[Item])
    assert got == want


def test_simple_array_with_simple_object_in_dataclass():
    @dataclass
    class Item:
        first_val: str = json_field(json="firstVal")
        datetime_key: datetime = json_field(json="datetimeKey")
        date_key: date = json_field(json="dateKey")

    @dataclass
    class Response:
        item_key: Item = json_field(json="itemKey")
        item_list: List[Item] = json_field(json="itemList")

    item = {
        "firstVal": "test",
        "secondVal": "foo",
        "datetimeKey": "2020-06-23T10:07:30+00:00",
        "dateKey": "2020-06-23",
    }
    json = {
        "itemKey": {**item},
        "itemList": [{**item}, {**item}],
    }

    item = Item(
        first_val="test",
        datetime_key=datetime(2020, 6, 23, 10, 7, 30, tzinfo=pytz.UTC),
        date_key=date(2020, 6, 23),
    )
    want = Response(item_key=item, item_list=[item, item])
    got = unmarshal(json, Response)

    assert got == want


def test_simple_array_with_multiple_simple_objects():
    @dataclass
    class Item:
        first_val: str = json_field(json="firstVal")

    json = [
        {"firstVal": "hello", "secondVal": "there"},
        {"firstVal": "test", "secondVal": "there"},
        {"firstVal": "var", "secondVal": "there"},
    ]

    want = [Item(first_val="hello"), Item(first_val="test"), Item(first_val="var")]
    got = unmarshal(json, List[Item])

    assert got == want


def test_simple_nesting_of_objects():
    @dataclass
    class Item:
        first_val: str = json_field(json="firstVal")

    @dataclass
    class Parent:
        item: Item = json_field(json="item")

    json = {"item": {"firstVal": "hello"}}

    want = Parent(item=Item(first_val="hello"))
    got = unmarshal(json, Parent)

    assert got == want


def test_simple_object_with_simple_array_item():
    @dataclass
    class Item:
        items: List[str] = json_field(json="items")

    json = {"items": ["elem1", "elem2", "elem3"]}

    want = Item(items=["elem1", "elem2", "elem3"])
    got = unmarshal(json, Item)

    assert got == want


def test_simple_object_with_nullable_key():
    @dataclass
    class Item:
        normal_val: str = json_field(json="normalVal")
        optional_val: Optional[str] = json_field(json="optionalVal")

    json = {"normalVal": "value", "optionalVal": None}

    want = Item(normal_val="value", optional_val=None)
    got = unmarshal(json, Item)

    assert got == want


def test_simple_optional_doesnt_require_data_in_json():
    @dataclass
    class Item:
        expected: int = json_field(json="expectedValue")
        maybe: Optional[float] = json_field(json="probablyNotThere")

    @dataclass
    class Response:
        items: List[Item]

    json = {
        "items": [
            {"expectedValue": 1002},
            {"expectedValue": 982, "probablyNotThere": 928.23},
            {"expectedValue": 282},
            {"expectedValue": 819},
        ]
    }

    want = Response(
        items=[
            Item(expected=1002, maybe=None),
            Item(expected=982, maybe=928.23),
            Item(expected=282, maybe=None),
            Item(expected=819, maybe=None),
        ]
    )
    got = unmarshal(json, Response)

    assert got == want


def test_simple_null_value():
    @dataclass
    class Item:
        val: None

    json = {"val": None}
    want = Item(val=None)
    got = unmarshal(json, Item)
    assert got == want


def test_simple_enum():
    class Colour(enum.Enum):
        RED = "RED"
        BLUE = "BLUE"

    json = "RED"

    want = Colour.RED
    got = unmarshal(json, Colour)
    assert got == want


def test_simple_object_with_enum():
    class Colour(enum.Enum):
        RED = "RED"
        BLUE = "BLUE"

    @dataclass
    class Item:
        desc: str
        colour: Colour

    json = [{"desc": "car", "colour": "RED"}, {"desc": "boat", "colour": "BLUE"}]
    got = unmarshal(json, List[Item])

    want = [
        Item(desc="car", colour=Colour.RED),
        Item(desc="boat", colour=Colour.BLUE),
    ]
    assert got == want


def test_simple_invalid_enum():
    class Colour(enum.Enum):
        RED = "RED"
        BLUE = "BLUE"

    json = "GREEN"

    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, Colour)
    assert str(exc_info.value) == "Unable to use data value 'GREEN' as Enum <enum 'Colour'>"


def test_simple_optional_enum_is_null():
    class Colour(enum.Enum):
        RED = "RED"
        BLUE = "BLUE"

    @dataclass
    class Item:
        value: Optional[Colour]

    json = {"value": None}

    got = unmarshal(json, Item)
    want = Item(value=None)
    assert got == want


def test_simple_optional_enum_is_valid():
    class Colour(enum.Enum):
        RED = "RED"
        BLUE = "BLUE"

    @dataclass
    class Item:
        value: Optional[Colour]

    json = {"value": "RED"}

    got = unmarshal(json, Item)
    want = Item(value=Colour.RED)
    assert got == want


def test_simple_optional_datetime_is_null():
    @dataclass
    class Item:
        value: Optional[datetime]

    json = {"value": None}

    got = unmarshal(json, Item)
    want = Item(value=None)
    assert got == want


def test_simple_optional_datetime_is_valid():
    @dataclass
    class Item:
        value: Optional[datetime]

    json = {"value": "2020-06-23T07:59:30+00:00"}

    got = unmarshal(json, Item)
    want = Item(value=datetime(2020, 6, 23, 7, 59, 30, tzinfo=pytz.UTC))
    assert got == want


def test_simple_optional_date_is_null():
    @dataclass
    class Item:
        value: Optional[date]

    json = {"value": None}

    got = unmarshal(json, Item)
    want = Item(value=None)
    assert got == want


def test_simple_optional_date_is_valid():
    @dataclass
    class Item:
        value: Optional[date]

    json = {"value": "2020-06-23"}

    got = unmarshal(json, Item)
    want = Item(value=date(2020, 6, 23))
    assert got == want


def test_simple_union():
    @dataclass
    class Item:
        value: Union[None, int]

    json = {"value": 120}

    want = Item(value=120)
    got = unmarshal(json, Item)
    assert got == want


@pytest.mark.parametrize(
    "timestamp",
    [
        "2020-06-22T08:55:05+00:00",
        "2020-06-22T08:55:05.000+00:00",
        "2020-06-22T08:55:05.000000+00:00",
        "2020-06-22T08:55:05Z",
        "2020-06-22T08:55:05.000Z",
        "2020-06-22T08:55:05.000000Z",
    ],
)
def test_simple_datetime(timestamp):
    @dataclass
    class Item:
        value: datetime

    json = {"value": timestamp}

    want = Item(value=datetime(2020, 6, 22, 8, 55, 5, tzinfo=pytz.UTC))
    got = unmarshal(json, Item)
    assert got == want


def test_simple_datetime_optional_valid():
    @dataclass
    class Item:
        value: Optional[datetime]

    json = {"value": "2020-06-22T08:55:05+00:00"}

    want = Item(value=datetime(2020, 6, 22, 8, 55, 5, tzinfo=pytz.UTC))
    got = unmarshal(json, Item)
    assert got == want


def test_simple_datetime_optional_null():
    @dataclass
    class Item:
        value: Optional[datetime]

    json = {"value": None}

    want = Item(value=None)
    got = unmarshal(json, Item)
    assert got == want


def test_simple_datetime_explicit_format():
    @dataclass
    class Item:
        value: datetime

    json = {"value": "2020/05/27 (09:34:36)"}

    want = Item(value=datetime(2020, 5, 27, 9, 34, 36))
    got = unmarshal(json, Item, datetime_fmt="%Y/%m/%d (%H:%M:%S)")
    assert got == want


def test_simple_date():
    @dataclass
    class Item:
        value: date

    json = {"value": "2020-06-22"}

    want = Item(value=date(2020, 6, 22))
    got = unmarshal(json, Item)
    assert got == want


def test_simple_date_optional_valid():
    @dataclass
    class Item:
        value: Optional[date]

    json = {"value": "2020-06-22"}

    want = Item(value=date(2020, 6, 22))
    got = unmarshal(json, Item)
    assert got == want


def test_simple_date_optional_null():
    @dataclass
    class Item:
        value: Optional[date]

    json = {"value": None}

    want = Item(value=None)
    got = unmarshal(json, Item)
    assert got == want


def test_simple_date_explicit_format():
    @dataclass
    class Item:
        value: date

    json = {"value": "2020/11/02"}

    want = Item(value=date(2020, 11, 2))
    got = unmarshal(json, Item, date_fmt="%Y/%m/%d")
    assert got == want


def test_simple_uuid():
    @dataclass
    class Item:
        value: UUID

    json = {"value": "cb637f6a-0dc0-4c42-8764-5b98137a8ea6"}

    want = Item(value=UUID("cb637f6a-0dc0-4c42-8764-5b98137a8ea6"))
    got = unmarshal(json, Item)
    assert got == want


@pytest.mark.parametrize("invalid_uuid", ["cb637f6a", 123, 42.12, None])
def test_simple_uuid_is_invalid(invalid_uuid):
    @dataclass
    class Item:
        value: UUID

    json = {"value": invalid_uuid}
    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, Item)
    assert str(exc_info.value) == f"Unable to use data value '{invalid_uuid}' as UUID <class 'uuid.UUID'>"


def test_simple_uuid_optional_valid():
    @dataclass
    class Item:
        value: Optional[UUID]

    json = {"value": "cb637f6a-0dc0-4c42-8764-5b98137a8ea6"}

    want = Item(value=UUID("cb637f6a-0dc0-4c42-8764-5b98137a8ea6"))
    got = unmarshal(json, Item)
    assert got == want


def test_simple_uuid_optional_null():
    @dataclass
    class Item:
        value: Optional[UUID]

    json = {"value": None}

    want = Item(value=None)
    got = unmarshal(json, Item)
    assert got == want


def test_simple_uuid_array():
    @dataclass
    class Item:
        value: List[UUID]

    json = {"value": ["cb637f6a-0dc0-4c42-8764-5b98137a8ea6"]}

    want = Item(value=[UUID("cb637f6a-0dc0-4c42-8764-5b98137a8ea6")])
    got = unmarshal(json, Item)
    assert got == want


def test_simple_bool():
    @dataclass
    class Item:
        value: bool

    json = {"value": False}

    want = Item(value=False)
    got = unmarshal(json, Item)
    assert got == want


@pytest.mark.parametrize("invalid_bool", ["cb637f6a", 123, 42.12, None, "True", "False", 0, 1])
def test_simple_bool_is_invalid(invalid_bool):
    @dataclass
    class Item:
        value: bool

    json = {"value": invalid_bool}
    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, Item)
    want = (
        f"Invalid schema. schema = <class 'bool'>, data = '{invalid_bool}' "
        f"({type(invalid_bool)}) at location = value"
    )
    assert str(exc_info.value) == want


def test_simple_bool_optional_valid():
    @dataclass
    class Item:
        value: Optional[bool]

    json = {"value": True}

    want = Item(value=True)
    got = unmarshal(json, Item)
    assert got == want


def test_simple_bool_optional_null():
    @dataclass
    class Item:
        value: Optional[bool]

    json = {"value": None}

    want = Item(value=None)
    got = unmarshal(json, Item)
    assert got == want


def test_simple_bool_array():
    @dataclass
    class Item:
        value: List[bool]

    json = {"value": [True, False, True]}

    want = Item(value=[True, False, True])
    got = unmarshal(json, Item)
    assert got == want


@pytest.mark.parametrize("json,container", [("foo", str), (123, int), (456.829, float)])
def test_works_with_primitives(json, container):
    # primitives should return the original result

    got = unmarshal(json, container)
    assert got == json


def test_dataclass_invalid_for_json_types():
    # we do not accept a union other than optional includes a type of list or dict.
    # json structure needs to be explicit.
    @dataclass
    class DictItem:
        val: Union[str, dict]

    @dataclass
    class ListItem:
        val: Union[str, list]

    json = {"val": "hello"}

    want = (
        "Schemas defined with unions containing anything other than optional "
        "(NoneType + other) fields are not currently supported. Got "
        "typing.Union[str, dict]  with  (<class 'str'>, <class 'dict'>)"
    )
    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, DictItem)
    assert str(exc_info.value) == want

    want = (
        "Schemas defined with unions containing anything other than optional "
        "(NoneType + other) fields are not currently supported. Got "
        "typing.Union[str, list]  with  (<class 'str'>, <class 'list'>)"
    )
    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, ListItem)
    assert str(exc_info.value) == want


def test_unexpected_type_in_union():
    @dataclass
    class Item:
        val: Union[None, int]

    json = {"val": "test"}

    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, Item)
    want = (
        "Invalid schema. schema = typing.Union[NoneType, int], data = "
        "'test' (<class 'str'>) at location = val"
    )
    assert str(exc_info.value) == want


def test_unexpected_type():
    @dataclass
    class Item:
        val: str

    json = {"val": 1.234}

    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, Item)
    want = "Invalid schema. schema = <class 'str'>, data = '1.234' " "(<class 'float'>) at location = val"
    assert str(exc_info.value) == want


def test_item_not_present_in_json():
    @dataclass
    class Item:
        val: str
        other_val: str = json_field(json="otherVal")

    json = {"val": "test"}

    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, Item)
    want = "Expected json key is not present in object at position ''. 'otherVal' not in ['val']"
    assert str(exc_info.value) == want


def test_unknown_datatype():
    class Impossible:
        pass

    @dataclass
    class Item:
        first_value: float = json_field(json="firstValue")
        second_value: Impossible = json_field(json="secondValue")

    json = {"firstValue": 123.213, "secondValue": 999}

    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(json, Item)
    assert str(exc_info.value) == f"Schema type '{Impossible}' is not currently supported."
