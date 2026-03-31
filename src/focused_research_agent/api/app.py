from fastapi import FastAPI
from focused_research_agent.api.routers.research import research_router
from focused_research_agent.api.routers.health import health_router

'''
FastAPI application entrypoint for the Focused Research Agent.

This module creates the FastAPI app instance and registers API routers.
It acts as the HTTP entrypoint for the project and keeps the API bootstrap
logic thin and centralized.

Architecturally, this file belongs to the transport layer. It should focus
on app construction, router registration, and API-level configuration, while
delegating request handling to routers and business/use-case execution to the
application layer.
'''
app = FastAPI(title="Focused Research Agent API")

app.include_router(health_router)
app.include_router(research_router)