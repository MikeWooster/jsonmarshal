import json as _json
import os

from tests.fixtures.collected_data.dataclass import CollectedData, expected

DIRNAME = os.path.dirname(__file__)

with open(os.path.join(DIRNAME, "collected_data.json"), "r") as buf:
    json = _json.loads(buf.read())

__all__ = [json, expected, CollectedData]
