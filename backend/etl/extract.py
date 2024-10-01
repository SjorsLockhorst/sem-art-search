from loguru import logger

from config import settings
from db.crud import check_count_art_objects
from etl.errors import ExtractError
from etl.rijksmuseum.wrapper import Client, DescriptionLanguages


def fetch_art_objects(api_key: str, language: DescriptionLanguages = DescriptionLanguages.EN):
    """
    Fetch the art objects from the Rijksmuseum API.
    """
    try:
        client = Client(language=language, api_key=api_key)
        return client.get_all_objects_with_image()
    except Exception as e:
        raise ExtractError(msg=str(e))


def run_extract_stage():
    """
    Main function to retrieve and process art objects.
    """
    try:
        logger.info("Starting the full ETL process")
        logger.info("Checking current count of art objects")
        # TODO: Implement count check and maybe a limit to prevent fetching exisiting records
        logger.info(f"Current count is {check_count_art_objects()}")
        fetch_art_objects(settings.rijksmuseum_api_key)

    except ExtractError as e:
        logger.error(f"Data Extraction Error: {e}")
        raise

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise ExtractError(str(e))


if __name__ == "__main__":
    run_extract_stage()
