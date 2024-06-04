import asyncio
import os

from dotenv import load_dotenv

from src.etl.errors import MissingApiKeyError
from src.etl.rijksmuseum.wrapper import Client, DescriptionLanguages

load_dotenv()


async def main():
    api_key = os.getenv("RIJKSMUSEUM_API_KEY")

    if not api_key:
        raise MissingApiKeyError("No API Key found in the env variables")

    c = Client(language=DescriptionLanguages.NL, api_key=api_key)
    # art_objects = await c.get_initial_10_000_objects()


if __name__ == "__main__":
    asyncio.run(main())
