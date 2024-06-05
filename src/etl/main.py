from extract import main as run_extract
from embed import main as run_embed
import logging


async def main():
    logging.info("Starting the full ETL process")
    logging.info("Extracting ArtObjects")
    await run_extract()
    logging.info("Finished extracting ArtObjects")
    logging.info("Starting embeding of ArtObjects")
    await run_embed()
    logging.info("Finished embeding and saving of ArtObjects")
