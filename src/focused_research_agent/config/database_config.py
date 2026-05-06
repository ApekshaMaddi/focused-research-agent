"""
Database configuration for the Focused Research Agent.

This module defines database connection settings used by the SQLAlchemy
engine. It keeps database-specific configuration in one place, following
the same pattern as api_config.py and llm_config.py.

Architecturally, this module belongs to the configuration layer. It
provides the database URL to the database layer while remaining separate
from models, queries, and application logic.

The DATABASE_URL follows SQLAlchemy's connection string format:
- SQLite (local):    sqlite:///./research_agent.db
- PostgreSQL (prod): postgresql://user:password@host/dbname

Switching databases requires only changing the DATABASE_URL environment
variable. No application code changes are needed.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DatabaseSettings:
    """
    Structured database settings used by the SQLAlchemy engine.

    Attributes:
        database_url: SQLAlchemy connection string for the database.
            Defaults to a local SQLite file if not set in the environment.
    """

    database_url: str


def get_database_settings() -> DatabaseSettings:
    """
    Load database settings from environment variables with a sensible
    default.

    Defaults to a local SQLite file named research_agent.db in the
    project root if DATABASE_URL is not set in the environment.

    Returns:
        DatabaseSettings: Fully constructed database settings object.
    """
    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:///./research_agent.db",
    )

    return DatabaseSettings(database_url=database_url)
