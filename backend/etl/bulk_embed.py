import argparse
import os
import time
from multiprocessing import Pool

from loguru import logger

from db.crud import retrieve_unembedded_image_art
from etl.embed.embed import _run_embed_stage, batched
from etl.embed.models import get_image_embedder

NUM_THREADS_PER_PROC = 3

def process_batch(args):
    id_url_pairs, retrieval_batch_size, embedding_batch_size = args
    image_embedder = get_image_embedder()
    _run_embed_stage(id_url_pairs, image_embedder, retrieval_batch_size, embedding_batch_size)


def embed_in_parallel(total_amount: int, num_processes: int, retrieval_batch_size: int, embedding_batch_size: int):
    """Embed images in multiple processes at the same time."""
    logger.info("Starting batch processing")

    start = time.time()
    unembedded_art = retrieve_unembedded_image_art(total_amount)
    if num_processes == -1:
        # Each process has 3 threads, so we want to spin up
        num_processes = os.cpu_count() // NUM_THREADS_PER_PROC
        logger.info("num_processes is passed -1, so using all logical cores")
    logger.info(f"total_amount: {total_amount}")
    logger.info(f"num_processes: {num_processes}")
    logger.info(f"retrieval_batch_size: {retrieval_batch_size}")
    logger.info(f"embedding_batch_size: {embedding_batch_size}")

    # Each process will get an equal chunk of the output
    batch_size = total_amount // num_processes
    batches = list(batched(unembedded_art, batch_size))
    logger.info(f"Amount of batches: {len(batches)}.")
    logger.info(f"batch_size: {batch_size}.")

    process_args = [(batch, retrieval_batch_size, embedding_batch_size) for batch in batches]

    with Pool(num_processes) as pool:
        pool.map(process_batch, process_args)

    end = time.time()
    logger.info(f"Total processing time: {end - start} seconds, to process {len(unembedded_art)} embeddings.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run embedding in parallel using multiprocessing")
    parser.add_argument("total_amount", type=int, help="Total number of images to retrieve and embed")
    parser.add_argument("num_processes", type=int, help="Number of parallel processes to run")
    parser.add_argument("retrieval_batch_size", type=int, help="Batch size for retrieving images")
    parser.add_argument("embedding_batch_size", type=int, help="Batch size for embedding images")
    args = parser.parse_args()

    total_amount = args.total_amount
    num_processes = args.num_processes
    retrieval_batch_size = args.retrieval_batch_size
    embedding_batch_size = args.embedding_batch_size

    embed_in_parallel(total_amount, num_processes, retrieval_batch_size, embedding_batch_size)
