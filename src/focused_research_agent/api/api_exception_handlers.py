"""
Centralized FastAPI exception handlers for the Focused Research Agent API.

This module contains HTTP-specific exception handling logic for the API
layer. It converts shared application exceptions and unexpected runtime
exceptions into consistent HTTP JSON error responses.

Architecturally, this module belongs to the API layer because formatting
exceptions as HTTP responses is a transport concern, not an application or
workflow concern.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from focused_research_agent.application.exceptions import ApplicationError

logger = logging.getLogger("focused_research_agent.api.exception_handlers")


def _build_error_response(
    status_code: int,
    error: str,
    detail: str,
    path: str,
) -> JSONResponse:
    """
    Build a consistent JSON error response for the API layer.

    Args:
        status_code: HTTP status code to return.
        error: Short error category label.
        detail: Human-readable error detail.
        path: Request path where the error occurred.

    Returns:
        JSONResponse: Structured JSON error response.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "error": error,
            "detail": detail,
            "path": path,
        },
    )


def handle_application_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Convert an application-layer error into an HTTP 400 response.

    This handler is registered specifically for ApplicationError, even though
    the exception parameter is typed as Exception to satisfy FastAPI's broader
    exception-handler typing expectations.

    Args:
        request: Incoming FastAPI request object.
        exc: Exception raised during application/use-case execution.

    Returns:
        JSONResponse: Structured HTTP 400 response describing the handled
        application error.
    """
    return _build_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error="application_error",
        detail=str(exc),
        path=str(request.url.path),
    )


def handle_unexpected_exception(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Convert an unexpected server-side exception into an HTTP 500 response.

    Args:
        request: Incoming FastAPI request object.
        exc: Unexpected exception that bubbled up to the API boundary.

    Returns:
        JSONResponse: Structured HTTP 500 response with a safe generic error
        message.
    """
    logger.exception("Unexpected API error on path %s", request.url.path)

    return _build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="internal_server_error",
        detail="An unexpected internal error occurred",
        path=str(request.url.path),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register centralized exception handlers on the FastAPI app.

    Args:
        app: FastAPI application instance.

    Returns:
        None
    """
    app.add_exception_handler(ApplicationError, handle_application_error)
    app.add_exception_handler(Exception, handle_unexpected_exception)