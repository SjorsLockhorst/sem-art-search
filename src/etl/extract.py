import asyncio
import os
import logging
from dotenv import load_dotenv

from src.etl.errors import MissingApiKeyError, ExtractError
from src.etl.rijksmuseum.wrapper import Client, DescriptionLanguages
from src.db.crud import check_count_art_objects

load_dotenv()


def get_api_key(env_var: str) -> str:
    """
    Retrieve the API key from environment variables.
    """
    api_key = os.getenv(env_var)
    if not api_key:
        raise MissingApiKeyError("No API Key found in the env variable")
    return api_key


# During the MVP phase this is limited to a subset of 10,000 objects
async def fetch_art_objects(
    api_key: str, language: DescriptionLanguages = DescriptionLanguages.NL
):
    """
    Fetch the initial 10,000 art objects from the Rijksmuseum API.
    """
    try:
        client = Client(language=language, api_key=api_key)
        return await client.get_initial_10_000_objects()
    except Exception as e:
        raise ExtractError(msg=str(e))


async def main():
    """
    Main function to retrieve and process art objects.
    """
    try:
        api_key = get_api_key("RIJKSMUSEUM_API_KEY")
        current_count_art_objects = check_count_art_objects()

        # After MVP this can be increased or removed
        if current_count_art_objects >= 10_000:
            logging.info(
                "Initial 10,000 objects already in the database. Stopping ETL during MVP phase"
            )
            return

        art_objects = await fetch_art_objects(api_key)
        logging.info(f"Extracted {len(art_objects)} art objects")

    except MissingApiKeyError as e:
        logging.error(f"API Key Error: {e}")
        raise
    except ExtractError as e:
        logging.error(f"Data Extraction Error: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise ExtractError(str(e))
