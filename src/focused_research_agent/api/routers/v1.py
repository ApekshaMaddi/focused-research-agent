"""
Versioned API router grouping for the Focused Research Agent.

This module defines the version-1 API namespace and attaches versioned
feature routers under a shared prefix. It keeps API versioning as a transport
layer concern and avoids hardcoding version prefixes directly into every
feature route.

Architecturally, this module belongs to the API layer because versioned route
grouping is an HTTP/API contract concern, not an application, workflow, or
provider concern.
"""

from fastapi import APIRouter

from focused_research_agent.api.routers.research import research_router


def create_v1_router() -> APIRouter:
    """
    Build the version-1 API router group.

    This function creates an API router with the shared `/api/v1` prefix and
    mounts versioned feature routers under that namespace.

    Returns:
        APIRouter: Version-1 grouped API router.
    """
    router = APIRouter(prefix="/api/v1")
    router.include_router(research_router)
    return router


api_v1_router = create_v1_router()