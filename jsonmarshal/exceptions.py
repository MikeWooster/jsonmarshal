"""Exceptions raised by jsonmarshal"""


class UnmarshalError(Exception):
    """Error when unmarshalling data from json to dataclasses."""


class MarshalError(Exception):
    """Error when marshalling data from dataclasses to json."""
