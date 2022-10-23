import asyncio

import aiohttp
import asyncpg
import pytest
import pytest_asyncio
from loguru import logger

from .settings import TEST_SETTINGS
from .testdata.db_data_test import postgres_current_tables_names
from .utils.wait_db import wait_postgres_db


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="session")
async def db_postgres_connection():
    """Fixture to wait for the database to be ready."""
    await wait_postgres_db()
    async_pg_connection = await asyncpg.connect(TEST_SETTINGS.database_dsn)

    yield async_pg_connection
    await async_pg_connection.close()
    print("\n")
    logger.info("Postgres connection is closed")


@pytest_asyncio.fixture(scope="session")
async def aiohttp_session():
    """Fixture to create an aiohttp session."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def postgres_tables_names(db_postgres_connection):
    """Fixture to get the names of all tables in the database."""
    tables_names = await db_postgres_connection.fetch(
        f"""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        AND table_schema IN('{TEST_SETTINGS.POSTGRES_SCHEMA}')
        """
    )
    return (
        tuple(table["table_name"] for table in tables_names),
        postgres_current_tables_names,
    )
