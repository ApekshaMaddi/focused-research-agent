"""
Pytest configuration for the Focused Research Agent test suite.

Sets DATABASE_URL to a shared in-memory SQLite database before any
test module is imported. Using a shared cache URI ensures all
connections within the test session see the same database and the
same tables, avoiding the 'no such table' error that occurs when
each connection gets its own isolated in-memory database.
"""

import os

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///file::memory:?cache=shared&uri=true",
)


def pytest_configure(config):
    """
    Create all database tables after environment variables are set
    and before any tests run.

    Args:
        config: The pytest configuration object.
    """
    from focused_research_agent.database.database import init_db

    init_db()
