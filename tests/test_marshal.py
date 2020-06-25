from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

import pytest
import pytz

from jsonmarshal import json_field
from jsonmarshal.exceptions import MarshalError
from jsonmarshal.marshal import marshal
from tests.fixtures import load_fixtures


@pytest.mark.parametrize(
    "fixture_name,marshalled,schema,unmarshalled,date_fmt,datetime_fmt", load_fixtures()
)
def test_marshal_integration(fixture_name, marshalled, schema, unmarshalled, date_fmt, datetime_fmt):
    got = marshal(unmarshalled, date_fmt=date_fmt, datetime_fmt=datetime_fmt)
    assert got == marshalled


def test_simple_dataclass_optional_valid():
    class Option(Enum):
        ONE = "ONE"
        TWO = "TWO"

    @dataclass
    class Item:
        string_value: Optional[str] = json_field(json="stringValue")
        int_value: Optional[int] = json_field(json="intValue")
        float_value: Optional[float] = json_field(json="floatValue")
        bool_value: Optional[bool] = json_field(json="boolValue")
        null_value: Optional[None] = json_field(json="nullValue")
        datetime_value: Optional[datetime] = json_field(json="datetimeValue")
        date_value: Optional[date] = json_field(json="dateValue")
        uuid_value: Optional[UUID] = json_field(json="uuidValue")
        enum_value: Optional[Option] = json_field(json="enumValue")

    data = Item(
        string_value="hello",
        int_value=1,
        float_value=12.12,
        bool_value=True,
        null_value=None,
        datetime_value=datetime(2020, 6, 23, 11, 12, 13, tzinfo=pytz.UTC),
        date_value=date(2020, 6, 24),
        uuid_value=UUID("7499af75-0d01-42a9-a6d7-1c45c1d22125"),
        enum_value=Option.TWO,
    )
    got = marshal(data)
    want = {
        "stringValue": "hello",
        "intValue": 1,
        "floatValue": 12.12,
        "boolValue": True,
        "nullValue": None,
        "datetimeValue": "2020-06-23T11:12:13+00:00",
        "dateValue": "2020-06-24",
        "uuidValue": "7499af75-0d01-42a9-a6d7-1c45c1d22125",
        "enumValue": "TWO",
    }
    assert got == want


def test_simple_dataclass_optional_null():
    class Option(Enum):
        ONE = "ONE"
        TWO = "TWO"

    @dataclass
    class Item:
        string_value: Optional[str] = json_field(json="stringValue")
        int_value: Optional[int] = json_field(json="intValue")
        float_value: Optional[float] = json_field(json="floatValue")
        bool_value: Optional[bool] = json_field(json="boolValue")
        null_value: Optional[None] = json_field(json="nullValue")
        datetime_value: Optional[datetime] = json_field(json="datetimeValue")
        date_value: Optional[date] = json_field(json="dateValue")
        uuid_value: Optional[UUID] = json_field(json="uuidValue")
        enum_value: Optional[Option] = json_field(json="enumValue")

    data = Item(
        string_value=None,
        int_value=None,
        float_value=None,
        bool_value=None,
        null_value=None,
        datetime_value=None,
        date_value=None,
        uuid_value=None,
        enum_value=None,
    )
    got = marshal(data)
    want = {
        "stringValue": None,
        "intValue": None,
        "floatValue": None,
        "boolValue": None,
        "nullValue": None,
        "datetimeValue": None,
        "dateValue": None,
        "uuidValue": None,
        "enumValue": None,
    }
    assert got == want


def test_simple_nested_dataclass():
    @dataclass
    class Inner:
        string_value: str = json_field(json="stringValue")
        int_value: int = json_field(json="intValue")
        uuid_value: UUID = json_field(json="uuidValue")

    @dataclass
    class Item:
        inner: Inner

    data = Item(
        inner=Inner(
            string_value="hello", int_value=123, uuid_value=UUID("8308ce66-f250-4235-9718-39f48e16a9ae")
        )
    )
    got = marshal(data)
    want = {
        "inner": {
            "stringValue": "hello",
            "intValue": 123,
            "uuidValue": "8308ce66-f250-4235-9718-39f48e16a9ae",
        }
    }
    assert got == want


def test_simple_array():
    data = ["string", "string2", "string3"]
    got = marshal(data)
    assert got == data


def test_simple_array_of_dataclasses():
    class Option(Enum):
        ONE = "ONE"
        TWO = "TWO"

    @dataclass
    class Item:
        string_value: str = json_field(json="stringValue")
        int_value: int = json_field(json="intValue")
        float_value: float = json_field(json="floatValue")
        bool_value: bool = json_field(json="boolValue")
        null_value: None = json_field(json="nullValue")
        datetime_value: datetime = json_field(json="datetimeValue")
        date_value: date = json_field(json="dateValue")
        uuid_value: UUID = json_field(json="uuidValue")
        enum_value: Option = json_field(json="enumValue")

    data = [
        Item(
            string_value="hello",
            int_value=1,
            float_value=12.12,
            bool_value=True,
            null_value=None,
            datetime_value=datetime(2020, 6, 23, 11, 12, 13, tzinfo=pytz.UTC),
            date_value=date(2020, 6, 24),
            uuid_value=UUID("7499af75-0d01-42a9-a6d7-1c45c1d22125"),
            enum_value=Option.TWO,
        ),
        Item(
            string_value="there",
            int_value=1,
            float_value=12.12,
            bool_value=True,
            null_value=None,
            datetime_value=datetime(2020, 6, 23, 11, 12, 13, tzinfo=pytz.UTC),
            date_value=date(2020, 6, 24),
            uuid_value=UUID("7499af75-0d01-42a9-a6d7-1c45c1d22125"),
            enum_value=Option.TWO,
        ),
    ]
    got = marshal(data)
    want = [
        {
            "stringValue": "hello",
            "intValue": 1,
            "floatValue": 12.12,
            "boolValue": True,
            "nullValue": None,
            "datetimeValue": "2020-06-23T11:12:13+00:00",
            "dateValue": "2020-06-24",
            "uuidValue": "7499af75-0d01-42a9-a6d7-1c45c1d22125",
            "enumValue": "TWO",
        },
        {
            "stringValue": "there",
            "intValue": 1,
            "floatValue": 12.12,
            "boolValue": True,
            "nullValue": None,
            "datetimeValue": "2020-06-23T11:12:13+00:00",
            "dateValue": "2020-06-24",
            "uuidValue": "7499af75-0d01-42a9-a6d7-1c45c1d22125",
            "enumValue": "TWO",
        },
    ]
    assert got == want


def test_error_when_trying_to_marshal_unexpected_type():
    class Custom:
        pass

    @dataclass
    class Item:
        my_type: Custom

    c = Custom()
    data = Item(my_type=c)

    with pytest.raises(MarshalError) as exc_info:
        marshal(data)

    want = f"Unable to marshal data '{c}' ({type(c)}) to known type."
    got = str(exc_info.value)
    assert got == want


def test_simple_array_field():
    @dataclass
    class Item:
        value: str

    @dataclass
    class Response:
        items: List[Item]

    data = Response(items=[Item(value="hello"), Item(value="there")])
    want = {"items": [{"value": "hello"}, {"value": "there"}]}
    got = marshal(data)
    assert got == want


def test_nested_dict_lists():
    # testing multiple nestings
    @dataclass
    class Event:
        desc: str
        attendees: int

    @dataclass
    class Person:
        name: str
        events: List[Event]

    @dataclass
    class Result:
        people: List[Person]

    @dataclass
    class Data:
        result: Result

    data = Data(
        result=Result(
            people=[
                Person(
                    name="john",
                    events=[Event(desc="party", attendees=12), Event(desc="sleepover", attendees=2)],
                ),
                Person(
                    name="sarah",
                    events=[Event(desc="beach", attendees=21), Event(desc="stargazing", attendees=7)],
                ),
            ]
        )
    )
    got = marshal(data)
    want = {
        "result": {
            "people": [
                {
                    "name": "john",
                    "events": [{"desc": "party", "attendees": 12}, {"desc": "sleepover", "attendees": 2}],
                },
                {
                    "name": "sarah",
                    "events": [{"desc": "beach", "attendees": 21}, {"desc": "stargazing", "attendees": 7}],
                },
            ]
        }
    }
    assert got == want


def test_reusing_dataclass():
    @dataclass
    class Item:
        value: str
        count: int

    @dataclass
    class Response:
        first_item: Item
        second_item: Item
        items: List[Item]

    item = Item(value="itemval", count=100)
    data = Response(first_item=item, second_item=item, items=[item, item, item])

    got = marshal(data)
    want = {
        "first_item": {"value": "itemval", "count": 100},
        "second_item": {"value": "itemval", "count": 100},
        "items": [
            {"value": "itemval", "count": 100},
            {"value": "itemval", "count": 100},
            {"value": "itemval", "count": 100},
        ],
    }
    assert got == want


def test_omitempty():
    @dataclass
    class Item:
        value: str
        str_value: Optional[str] = json_field(omitempty=True)
        int_value: Optional[int] = json_field(omitempty=True)
        float_value: Optional[float] = json_field(omitempty=True)
        bool_value: Optional[bool] = json_field(omitempty=True)
        uuid_value: Optional[UUID] = json_field(omitempty=True)
        datetime_value: Optional[datetime] = json_field(omitempty=True)
        date_value: Optional[date] = json_field(omitempty=True)

    data = Item(
        value="present",
        str_value=None,
        int_value=None,
        float_value=None,
        bool_value=None,
        uuid_value=None,
        date_value=None,
        datetime_value=None,
    )

    got = marshal(data)
    want = {"value": "present"}
    assert got == want


def test_marshal_dates():
    @dataclass
    class Item:
        date_value: date

    data = Item(date_value=date(2020, 6, 23))
    got = marshal(data, date_fmt="%d %b %Y")
    want = {"date_value": "23 Jun 2020"}
    assert got == want


def test_marshal_datetimes():
    @dataclass
    class Item:
        datetime_value: datetime

    data = Item(datetime_value=datetime(2020, 6, 23, 11, 30, 12, tzinfo=pytz.UTC))
    got = marshal(data, datetime_fmt="%d %b %Y %H:%M")
    want = {"datetime_value": "23 Jun 2020 11:30"}
    assert got == want
