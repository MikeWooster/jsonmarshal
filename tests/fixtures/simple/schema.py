# Test that tries to combine all the usable types into one test.
# exercises the complexity of the unmarshalling.
import enum
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from jsonmarshal import json_field


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
class Schema(Item):
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
