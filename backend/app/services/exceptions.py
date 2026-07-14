"""Shared service exceptions."""


class SQLValidationError(ValueError):
    """Raised when generated SQL fails safety validation."""


class SQLExecutionError(RuntimeError):
    """Raised when validated SQL fails during execution."""
