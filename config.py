from pydantic_settings import BaseSettings, SettingsConfigDict

_base_setting = SettingsConfigDict(
    env_file="./.env", extra="ignore", env_ignore_empty=True
)


class DatabaseSettings(BaseSettings):
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int

    model_config = _base_setting

    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


db_settings = DatabaseSettings()
