import pytest


@pytest.mark.asyncio
class TestPostgresDB:
    async def test_connection(self, db_postgres_connection):
        assert db_postgres_connection.is_closed() is False

    async def test_tables_names(self, postgres_tables_names):
        db_tables_names, postgres_current_tables_names = postgres_tables_names
        assert len(db_tables_names) > 0
        assert db_tables_names == postgres_current_tables_names
