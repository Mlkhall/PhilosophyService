import asyncio
from typing import Tuple, Union, Dict

import asyncpg
import backoff
from loguru import logger

from ..core.config import PostgresSettings
from ..models.data_sources import CyberleninkaArticle
from ..utils.patterns import singleton


@singleton
class AsyncPostgresDB:
    postgres_settings = PostgresSettings()

    async def create_connection(self) -> asyncpg.Connection:
        return await asyncpg.connect(self.postgres_settings.database_dsn)

    async def close_connection(self) -> None:
        await self.connection.close()

    async def __aenter__(self) -> asyncpg.Connection:
        self.connection = await self.create_connection()
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close_connection()


class PostgresDBInterface:
    def __init__(self) -> None:
        self.client_async_pg = AsyncPostgresDB()

    async def get_tables(self) -> Tuple[str]:
        connection = await self.client_async_pg.create_connection()
        tables_names = await connection.execute(
            f"""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            AND table_schema IN('{self.client_async_pg.postgres_settings.postgres_url}')
            """,
        )
        return tuple(table["table_name"] for table in tables_names)

    async def get_schemas(self) -> Tuple[str]:
        async with self.client_async_pg as connection:
            schemas_names = await connection.fetch(
                """
                SELECT schema_name FROM information_schema.schemata
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
                """,
            )
            return tuple(schema["schema_name"] for schema in schemas_names)

    async def get_table_columns(self, table_name: str) -> Tuple[str]:
        connection = await self.client_async_pg.create_connection()
        table_columns = await connection.fetch(
            f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """,
        )
        return tuple(column["column_name"] for column in table_columns)

    async def check_row_exists(
        self, table_name: str, row_id: Union[int, str], column_name: str = "cyberleninka_id"
    ) -> Tuple[Union[str, int], bool]:
        connection = await self.client_async_pg.create_connection()
        return row_id, await connection.fetch(
            f"""
            SELECT EXISTS (
                SELECT 1 FROM {table_name}
                WHERE {column_name} = '{row_id}'
            )
            """
        )

    async def execute_query(self, query: str) -> None:
        connection = await self.client_async_pg.create_connection()
        try:
            return await connection.execute(query)
        except asyncpg.exceptions.UniqueViolationError:
            logger.error(f"UniqueViolationError: {query}")


class PostgresWriter:
    interface: PostgresDBInterface = PostgresDBInterface()

    async def write(self, table_name: str, table_data: Dict) -> None:
        columns = set(await self.interface.get_table_columns(table_name))
        query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join([f"'{table_data[column]}'" for column in columns])})
        """
        await self.interface.execute_query(query)

    @backoff.on_exception(backoff.expo, asyncpg.exceptions.ConnectionDoesNotExistError, max_tries=60)
    def write_demo_cyberleninka(self, articles: Tuple[CyberleninkaArticle, ...]) -> None:
        event_loop = asyncio.get_event_loop()
        tasks = asyncio.gather(
            *(self.write(table_name="demo_cyberleninka", table_data=article.postgresql_view) for article in articles),
        )
        event_loop.run_until_complete(tasks)

    @backoff.on_exception(backoff.expo, asyncpg.exceptions.ConnectionDoesNotExistError, max_tries=60)
    def check_rows_exists(
        self, table_name: str, rows_id: Tuple[str, ...], column_name: str = "cyberleninka_id"
    ) -> bool:
        event_loop = asyncio.get_event_loop()
        tasks = asyncio.gather(
            *(
                self.interface.check_row_exists(table_name=table_name, row_id=row, column_name=column_name)
                for row in rows_id
            ),
        )
        return event_loop.run_until_complete(tasks)
