import json
import os
from importlib import import_module
from typing import Any, List, Optional, Tuple

DIRNAME = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))


def load_json(filename):
    with open(filename) as buf:
        return json.loads(buf.read())


def load_fixtures() -> List[Tuple[str, Any, Any, Any, Optional[str], Optional[str]]]:
    # Returns a list of fixtures that can be used in parametrised tests
    # returns args:
    #  - fixture_name
    #  - marshalled (json)
    #  - schema (dataclass)
    #  - unmarshalled (dataclass instance)
    #  - date_fmt
    #  - datetime_fmt

    fixtures = []
    for fixture_name in os.listdir(DIRNAME):
        fixture_dir = os.path.join(DIRNAME, fixture_name)

        if not os.path.isdir(fixture_dir):
            continue

        if fixture_name.startswith("__") and fixture_name.endswith("__"):
            # Ignore dunders
            continue

        mod = import_module(f"tests.fixtures.{fixture_name}")

        try:
            marshalled = load_json(mod.marshalled)
            unmarshalled = mod.get_unmarshalled()
            schema = mod.Schema
        except Exception as e:
            raise RuntimeError(f"Failed to load fixture '{fixture_name}'") from e

        # Load date/datetime formats from the fixture (not requried)
        try:
            date_fmt = mod.date_fmt
        except AttributeError:
            date_fmt = None
        try:
            datetime_fmt = mod.datetime_fmt
        except AttributeError:
            datetime_fmt = None

        fixtures.append((fixture_name, marshalled, schema, unmarshalled, date_fmt, datetime_fmt))

    return fixtures
