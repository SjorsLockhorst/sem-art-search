from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    rijksmuseum_api_key: str


settings = Settings()  # type: ignore  # noqa: PGH003
