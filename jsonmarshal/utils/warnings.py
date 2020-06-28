import warnings


def _deprecation_warning(message: str) -> None:
    """Emit a deprecation warning."""
    warnings.warn(f"[jsonmarshal] {message}", DeprecationWarning)
