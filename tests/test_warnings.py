import pytest

from jsonmarshal.utils.warnings import _deprecation_warning


def test_deprecation_warning():
    with pytest.warns(DeprecationWarning) as record:
        _deprecation_warning("a warning")
    assert len(record) == 1
    # check that the message matches
    assert record[0].message.args[0] == "[jsonmarshal] a warning"
