import os

from tests.fixtures.simple.schema import Schema
from tests.fixtures.simple.unmarshalled import get_unmarshalled

DIRNAME = os.path.dirname(__file__)

marshalled = os.path.join(DIRNAME, "marshalled.json")

__all__ = [marshalled, Schema, get_unmarshalled]
