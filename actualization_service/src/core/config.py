from pydantic import BaseModel, BaseSettings, Field, PostgresDsn

from ..utils.patterns import singleton


@singleton
class PostgresSettings(BaseSettings):
    """Settings for the application."""

    default_port: int = 5431
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


@singleton
class ExternalSourcesSettings(BaseModel):
    """Settings for the application."""

    sources: dict[str, str] = Field(
        {
            "cyberleninka": "https://cyberleninka.ru/",
            "gtmarket": "https://gtmarket.ru/encyclopedia/",
            "philosophy": "https://www.philosophy.ru/library",
            "journals": "https://iphras.ru/journals.htm",
            "elibrary": "elibrary.ru",
            "habr": "habr.ru",
        },
    )

    @property
    def sources_names(self) -> tuple[str, ...]:
        """Database DSN."""
        return tuple(self.sources.keys())

    @property
    def sources_urls(
        self,
    ) -> tuple[str, ...]:
        """Database DSN."""
        return tuple(self.sources.values())
