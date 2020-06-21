import dataclasses


def json_field(*args, json: str = None, metadata: dict = None, **kwargs):
    """Extend dataclass field with an additional json argument.

    This will allow the user to specify the format of the key in json.
    """
    if metadata is None:
        metadata = {}
    metadata["json"] = json
    return dataclasses.field(*args, metadata=metadata, **kwargs)
