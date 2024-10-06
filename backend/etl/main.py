import asyncio

from loguru import logger

from etl.embed.embed import run_embed_stage
from etl.extract import run_extract_stage


async def main():
    logger.info("Extracting Art Objects from all sources")
    run_extract_stage()
    logger.info("Finished extracting ArtObjects")
    logger.info("Starting embedding of ArtObjects")
    # TODO: Discuss if this is the best palce to kick-off the embed process
    # await run_embed_stage(image_count=10_000, batch_size=8)
    logger.info("Finished embedding and saving of ArtObjects")


if __name__ == "__main__":
    asyncio.run(main())
