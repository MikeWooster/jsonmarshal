import dataclasses


def get_json_key(field: dataclasses.Field) -> str:
    """Given a json field, extract the key."""
    if field.metadata.get("json"):
        # The field is defined, we can just use this.
        return field.metadata["json"]

    return field.name
