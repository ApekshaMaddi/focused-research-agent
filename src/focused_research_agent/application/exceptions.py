"""
Shared application-layer exceptions for the Focused Research Agent.

This module defines exceptions that represent expected application/use-case
failures. These exceptions are transport-neutral and can be handled by
different entrypoints such as CLI, FastAPI, or future UI layers.

Architecturally, the exception class belongs to the application layer because
it represents business/use-case meaning, not HTTP, terminal, or UI behavior.
"""


class ApplicationError(Exception):
    """
    Represent an expected application/use-case failure.

    This exception is raised by the application layer when the research use
    case cannot proceed because of an expected input or business-level
    problem.

    Args:
        message: Human-readable description of the application error.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)