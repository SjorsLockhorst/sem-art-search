from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str


class EtlSettings(Settings):
    rijksmuseum_api_key: str


settings = Settings()  # type: ignore  # noqa: PGH003
