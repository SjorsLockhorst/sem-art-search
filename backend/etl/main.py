from loguru import logger

from etl.extract import run_extract_stage


def main():
    logger.info("Extracting Art Objects from all sources")
    run_extract_stage()
    logger.info("Finished extracting ArtObjects")


if __name__ == "__main__":
    main()
