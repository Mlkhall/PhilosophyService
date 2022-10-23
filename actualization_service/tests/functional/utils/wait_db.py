import asyncio

import asyncpg
from loguru import logger

from ..settings import TEST_SETTINGS


async def wait_postgres_db() -> None:
    """Wait for the database to be ready."""
    pg_connection = await asyncpg.connect(TEST_SETTINGS.database_dsn)
    while True:
        try:
            await pg_connection.execute("SELECT 1")
            logger.info("Postgres is ready")
            break
        except asyncpg.exceptions.CannotConnectNowError:
            logger.warning("Waiting for the database to be ready...")
            await asyncio.sleep(0.1)

    logger.success("Database is ready")
    await pg_connection.close()
