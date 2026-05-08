"""
FastAPI application entrypoint for the Focused Research Agent.

This module creates the FastAPI app instance, registers API routers, and
registers centralized exception handlers. It acts as the HTTP entrypoint for
the project and keeps app assembly logic centralized.

Architecturally, this file belongs to the transport layer. It should focus
on app construction and wiring while delegating request handling to routers
and use-case execution to the application layer.
"""

import logging
from fastapi import FastAPI

from focused_research_agent.api.api_exception_handlers import (
    register_exception_handlers,
)
from focused_research_agent.api.routers.health import health_router
from focused_research_agent.api.routers.v1 import api_v1_router
from focused_research_agent.config.api_config import get_api_settings
from focused_research_agent.database.database import init_db

logger = logging.getLogger(__name__)

def register_routers(app: FastAPI) -> None:
    """
    Register all API routers on the FastAPI app.

    This function mounts operational routes such as `/health` directly and
    mounts business/API contract routes through the versioned API namespace.

    Args:
        app: FastAPI application instance.

    Returns:
        None
    """
    app.include_router(health_router)
    app.include_router(api_v1_router)


def create_app() -> FastAPI:
    """
    Build and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI application.
    """
    settings = get_api_settings()

    app = FastAPI(
        title=settings.title,
        version=settings.version,
        debug=settings.debug,
    )

    init_db()
    logger.info(  # ← add
        "Application started. title=%s version=%s debug=%s",
        settings.title,
        settings.version,
        settings.debug,
    )

    register_routers(app)
    register_exception_handlers(app)

    logger.info("Routers and exception handlers registered.")

    return app
