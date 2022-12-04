import pytest
import validators

from actualization_service.core import ConfigFile
from actualization_service.core.config import (
    CollectorSettings,
    ExternalSourcesSettings,
    PostgresSettings,
)


@pytest.mark.asyncio
class TestExternalSourcesSettings:
    async def test_singleton(self):
        assert ExternalSourcesSettings() is ExternalSourcesSettings()

    async def test_sources_names(self, config_sources_names):
        settings = ExternalSourcesSettings()
        assert settings.sources_names == config_sources_names

    async def test_sources_urls(self, config_sources_urls):
        settings = ExternalSourcesSettings()
        assert settings.sources_urls == config_sources_urls

    async def test_sources_urls_type(self):
        settings = ExternalSourcesSettings()
        assert all(validators.url(url) for url in settings.sources_urls)


@pytest.mark.asyncio
class TestPostgresSettings:
    async def test_singleton(self):
        assert PostgresSettings() is PostgresSettings()

    async def test_database_dsn_type(self):
        settings = PostgresSettings()
        assert settings.database_dsn.startswith("postgresql://")

    async def test_database_dsn_host(self):
        settings = PostgresSettings()
        assert settings.database_dsn.endswith(
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )

    async def test_database_dsn_credentials(self):
        settings = PostgresSettings()
        assert settings.database_dsn.startswith(
            f"postgresql://{settings.POSTGRES_NAME}:{settings.POSTGRES_PASSWORD}@",
        )


@pytest.mark.asyncio
class TestConfigFile:
    async def test_singleton(self):
        assert ConfigFile() is ConfigFile()

    async def test_toml(self):
        assert isinstance(ConfigFile().get_config_toml(), dict)


@pytest.mark.asyncio
class TestCollectorConfig:
    async def test_singleton(self):
        assert CollectorSettings() is CollectorSettings()

    async def test_fields(self):
        assert isinstance(CollectorSettings().TIMEOUT, int)
        assert CollectorSettings().TIMEOUT > 0
