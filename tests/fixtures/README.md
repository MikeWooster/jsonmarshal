# Test Fixtures

This provides a simple way to add new tests.  These will be exercised in
both a marshalling and unmarshalling direction.

1. Create a new python package under the `fixtures` directory.
2. Create the following files:
   - `__init__.py`
   - `marshalled.json`
   - `schema.py`
   - `unmarshalled.py`
3. Copy the raw json into `marshalled.json`
4. Define the dataclass `Schema` inside `schema.py` that is expected to match the raw json
5. Define a function named `get_unmarshalled()` inside `unmarshalled.py` and return a Schema
instance that will match the raw json.
6. Copy and complete the following code into `__init__.py`:
   ```
import os

from tests.fixtures.<your-fixture>.schema import Schema
from tests.fixtures.<your-fixture>.unmarshalled import get_unmarshalled

DIRNAME = os.path.dirname(__file__)

marshalled = os.path.join(DIRNAME, "marshalled.json")

__all__ = [marshalled, Schema, get_unmarshalled]

   ```