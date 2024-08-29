import asyncio

from dotenv import load_dotenv
from loguru import logger

from config import settings
from db.crud import check_count_art_objects
from etl.errors import ExtractError, MissingApiKeyError
from etl.rijksmuseum.wrapper import Client, DescriptionLanguages

load_dotenv()


# During the MVP phase this is limited to a subset of 10,000 objects
async def fetch_art_objects(api_key: str, language: DescriptionLanguages = DescriptionLanguages.EN):
    """
    Fetch the initial 10,000 art objects from the Rijksmuseum API.
    """
    try:
        client = Client(language=language, api_key=api_key)
        return await client.get_initial_10_000_objects()
    except Exception as e:
        raise ExtractError(msg=str(e))


async def run_extract_stage():
    """
    Main function to retrieve and process art objects.
    """
    try:
        current_count_art_objects = check_count_art_objects()

        # After MVP this can be increased or removed
        if current_count_art_objects >= 1_000:
            logger.info("Initial 10,000 objects already in the database. Stopping ETL during MVP phase")
            return

        art_objects = await fetch_art_objects(settings.rijksmuseum_api_key)
        logger.info(f"Extracted {len(art_objects)} art objects")

    except MissingApiKeyError as e:
        logger.error(f"API Key Error: {e}")
        raise
    except ExtractError as e:
        logger.error(f"Data Extraction Error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise ExtractError(str(e))


if __name__ == "__main__":
    asyncio.run(run_extract_stage())
