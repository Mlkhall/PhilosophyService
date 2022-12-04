from pydantic import BaseSettings, Field, PostgresDsn

from .utils.patterns import singleton


@singleton
class TestSettings(BaseSettings):
    """Settings for the application."""

    POSTGRES_NAME: str = Field("user", env="POSTGRES_NAME")
    POSTGRES_PASSWORD: str = Field("password", env="POSTGRES_PASSWORD")
    POSTGRES_SCHEMA: str = Field("philosophy", env="POSTGRES_SCHEMA")
    POSTGRES_HOST: str = Field("0.0.0.0", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5430, env="POSTGRES_PORT")
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

    class Config:
        """Settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


TEST_SETTINGS = TestSettings()
