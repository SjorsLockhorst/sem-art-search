import asyncio
from src.etl.extract import main as run_extract
from src.etl.embed import main as run_embed
import logging


async def main():
    logging.info("Starting the full ETL process")
    logging.info("Extracting ArtObjects")
    await run_extract()
    logging.info("Finished extracting ArtObjects")
    logging.info("Starting embeding of ArtObjects")
    await run_embed(count=10, batch_size=5)
    logging.info("Finished embeding and saving of ArtObjects")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
