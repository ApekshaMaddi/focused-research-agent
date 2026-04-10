"""
FastAPI application entrypoint for the Focused Research Agent.

This module creates the FastAPI app instance, registers API routers, and
registers centralized exception handlers. It acts as the HTTP entrypoint for
the project and keeps app assembly logic centralized.

Architecturally, this file belongs to the transport layer. It should focus
on app construction and wiring while delegating request handling to routers
and use-case execution to the application layer.
"""

from fastapi import FastAPI

from focused_research_agent.api.api_exception_handlers import (
    register_exception_handlers,
)
from focused_research_agent.api.routers.health import health_router
from focused_research_agent.api.routers.research import research_router


def register_routers(app: FastAPI) -> None:
    """
    Register all API routers on the FastAPI app.

    Args:
        app: FastAPI application instance.

    Returns:
        None
    """
    app.include_router(health_router)
    app.include_router(research_router)


def create_app() -> FastAPI:
    """
    Build and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI application.
    """
    app = FastAPI(title="Focused Research Agent API")
    register_routers(app)
    register_exception_handlers(app)
    return app


app = create_app()