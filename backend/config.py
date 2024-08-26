from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str


settings = Settings()  # type: ignore  # noqa: PGH003
