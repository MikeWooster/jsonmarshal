![Unit Tests](https://github.com/MikeWooster/jsonmarshal/workflows/Unit%20Tests/badge.svg)

# JSON Marshal

Marshal JSON to and from python dataclasses

## Json Field

To support unmarshalling from json `jsonmarshal` extends the existing
dataclass `field` with the following options:
 - "json" option specifies the string key to be used when
   marshalling/unmarshalling to/from json. When the "json" option
   is not specified, the key on the dataclass will be used.

 - "omitempty" option specifies that the field should be omitted
   from marshalling if the field is typed as an `Optional[...]` value,
   and is set to `None`.

## Marshal

Marshal python dataclasses into json.

```
marshal(data: Any, datetime_fmt: Optional[str] = None, date_fmt: Optional[str] = None) -> Any
```

Given a dataclass `X`, marshal it into a json serializable format.

The "datetime_fmt" option allows the user to specify the format to
use when marshalling a datetime object into a string.

The "date_fmt" option allows the user to specify the format to use
when marshalling a date object into a string.

Both "datetime_fmt" and "date_fmt" options use the strftime/strptime behaviour:
https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

## Unmarshal

Unmarshal a response containing loaded json (json.load(s)) into a specified dataclass schema.

```
unmarshal(response: Any, schema: T, datetime_fmt: Optional[str] = None, date_fmt: Optional[str] = None) -> T
```

The "datetime_fmt" option allows the user to specify the format to
use when unmarshalling a string into a datetime object.

The "date_fmt" option allows the user to specify the format to use
when unmarshalling a string into a date object.

Both "datetime_fmt" and "date_fmt" options use the strftime/strptime behaviour:
https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

## Examples:

A plain dataclass:
```
@dataclass
class Item:
    first_key: str
    second_key: int

item = Item(first_key: "hello", second_key: 100)

marshal(item)
{"first_key": "hello", "second_key": 100}
```

A dataclass defining the json option:
```
@dataclass
class Item:
    first_key: str = json_field(json="firstKey")
    second_key: int = json_field(json="secondKey")

item = Item(first_key: "hello", second_key: 100)

marshal(item)
{"firstKey": "hello", "secondKey": 100}
```

A dataclass defining the omitempty option:
```
@dataclass
class Item:
    first_key: Optional[str] = json_field(omitempty=True)
    second_key: Optional[int] = json_field(omitempty=True)

item = Item(first_key: None, second_key: 100)

marshal(item)
{"second_key": 100}
```

A dataclass supporting Enums:
```
class Colour(Enum):
    RED = "RED"
    GREEN = "GREEN"

@dataclass
class Item:
    first_key: Colour
    second_key: Colour

item = Item(first_key: Colour.RED", second_key: Colour.GREEN)

marshal(item)
{"first_key": "RED", "second_key": "GREEN"}
```

A dataclass with dates/datetimes:
```
@dataclass
class Item:
    first_key: datetime
    second_key: date

item = Item(first_key: datetime(2020, 6, 11, 14, 32), second_key: date(2020, 5, 14))

marshal(item)
{"first_key": "2020-06-11T14:32:00", "second_key": "2020-05-14"}
```

A dataclass with dates/datetime supporting custom formats:
```
@dataclass
class Item:
    first_key: datetime
    second_key: date

item = Item(first_key: datetime(2020, 6, 11, 14, 32), second_key: date(2020, 5, 14))

marshal(item, datetime_fmt="%d %b %Y %H:%M", date_fmt="%d %b %Y")
{"first_key": "11 Jun 2020 14:32", "second_key": "14 Jun 2020"}
```

UUIDs get automatically marshalled to UUID type
```
@dataclass
class Item:
    first_key: UUID

item = Item(first_key: UUID("8b302ccb-fd97-4ce0-823a-eddd9ec1247d"))

marshal(item)
{"first_key": "8b302ccb-fd97-4ce0-823a-eddd9ec1247d"}
```
