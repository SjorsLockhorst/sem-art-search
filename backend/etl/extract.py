from loguru import logger

from etl.errors import ExtractError
from etl.rijksmuseum.main import fetch_art_objects
from etl.sources import ArtSource

# Mapping of sources and their fetch functions
sources = {ArtSource.RIJKSMUSEUM: fetch_art_objects}


def run_extract_stage():
    """
    Main function to retrieve and process art objects.
    """
    try:
        for source, extract_func in sources.items():
            logger.info(f"Starting extraction for {source}")
            extract_func()

    except ExtractError as e:
        logger.error(f"Data Extraction Error: {e}")
        raise

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise ExtractError(str(e)) from e


if __name__ == "__main__":
    run_extract_stage()
