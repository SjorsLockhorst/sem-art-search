from dotenv import load_dotenv
import asyncio
from rijksmuseum.wrapper import Client, DescriptionLanguages
import os
from errors import MissingApiKeyError

load_dotenv()


async def main():
    api_key = os.getenv("RIJKSMUSEUM_API_KEY")

    if not api_key:
        raise MissingApiKeyError("No API Key found in the env variables")

    c = Client(language=DescriptionLanguages.NL, api_key=api_key)
    # art_objects = await c.get_initial_10_000_objects()

    # print(len(art_objects))
    # print(art_objects[0])


if __name__ == "__main__":
    asyncio.run(main())
