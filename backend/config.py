from dotenv import load_dotenv

from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    database_url: str
    rijksmuseum_api_key: str


settings = Settings()  # type: ignore  # noqa: PGH003
