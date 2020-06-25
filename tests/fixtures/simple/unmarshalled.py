from datetime import date, datetime

import pytz

from tests.fixtures.simple import Schema
from tests.fixtures.simple.schema import Item, Size


def get_unmarshalled() -> Schema:
    item = Item(
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
    return Schema(
        important_item=item,
        items_list=[item, item, item],
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
