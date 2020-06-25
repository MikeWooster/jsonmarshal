import warnings


def deprecation_warning(message: str) -> None:
    """Emit a deprecation warning."""
    warnings.warn(f"[jsonmarshal] {message}", DeprecationWarning)
