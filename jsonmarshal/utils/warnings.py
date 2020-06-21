import warnings


def deprecation_warning(message: str):
    """Emit a deprecation warning."""
    warnings.warn(f"[jsonmarshal] {message}", DeprecationWarning)
