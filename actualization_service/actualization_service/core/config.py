from pydantic import (
    BaseModel,
    BaseSettings,
    Field,
    HttpUrl,
    PositiveFloat,
    PositiveInt,
    PostgresDsn,
)

from ..utils.patterns import singleton
from . import CONFIG_TOML


@singleton
class PostgresSettings(BaseSettings):
    """Settings for the application."""

    default_port: int = 5430
    POSTGRES_NAME: str = Field("user", env="POSTGRES_NAME")
    POSTGRES_PASSWORD: str = Field("password", env="POSTGRES_PASSWORD")
    POSTGRES_SCHEMA: str = Field("philosophy", env="POSTGRES_SCHEMA")
    POSTGRES_HOST: str = Field("0.0.0.0", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default_port, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field("postgres", env="POSTGRES_DB")

    @property
    def database_dsn(self) -> PostgresDsn:
        """Database DSN."""
        return PostgresDsn.build(
            scheme="postgresql",
            user=self.POSTGRES_NAME,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=str(self.POSTGRES_PORT),
            path=f"/{self.POSTGRES_DB}",
        )

    @property
    def postgres_url(self) -> str:
        return "postgresql://{0}:{1}@{2}:{3}/{4}?search_path={5}".format(
            self.POSTGRES_NAME,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
            self.POSTGRES_SCHEMA,
        )

    class Config:
        """Settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


@singleton
class ExternalSourcesSettings(BaseModel):
    """Settings for the application."""

    sources: dict[str, HttpUrl] = CONFIG_TOML["sources"]

    @property
    def sources_names(self) -> tuple[str, ...]:
        return tuple(self.sources.keys())

    @property
    def sources_urls(
        self,
    ) -> tuple[str, ...]:
        return tuple(self.sources.values())


@singleton
class CollectorSettings(BaseSettings):
    """Settings for the application."""

    TIMEOUT: PositiveInt = 1000
    START_SLEEP_TIME: PositiveFloat = 1
    FACTOR: PositiveInt = 1
    BORDER_TIME_SLEEP: PositiveInt = 1000000


COLLECTOR_SETTINGS = CollectorSettings()
