import os

from tests.fixtures.collected_data.schema import Schema
from tests.fixtures.collected_data.unmarshalled import get_unmarshalled

DIRNAME = os.path.dirname(__file__)

marshalled = os.path.join(DIRNAME, "marshalled.json")

datetime_fmt = "%Y-%m-%d %H:%M:%S"

__all__ = [marshalled, Schema, get_unmarshalled]
