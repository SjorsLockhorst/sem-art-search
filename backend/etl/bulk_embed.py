import time
from multiprocessing import Pool

from loguru import logger

from db.crud import retrieve_unembedded_image_art
from etl.embed.embed import _run_embed_stage, batched
from etl.embed.models import get_image_embedder


# Wrapper function for each process, creates its own instance of ImageEmbedder
def process_batch(args):
    id_url_pairs, retrieval_batch_size, embedding_batch_size = args

    # Each process creates its own image_embedder
    image_embedder = get_image_embedder()

    # Now call the _run_embed_stage with the process's id_url_pairs and its own image_embedder
    _run_embed_stage(id_url_pairs, image_embedder, retrieval_batch_size, embedding_batch_size)

if __name__ == "__main__":
    logger.info("Starting batch processing")
    start = time.time()

    COUNT = 100  # Total number of images to embed
    NUM_PROCS = 2  # Number of parallel processes to run

    retrieval_batch_size = 8  # Size of image retrieval batch
    embedding_batch_size = 8  # Size of image embedding batch

    unembedded_art = retrieve_unembedded_image_art(COUNT)

    batch_size = COUNT // NUM_PROCS
    batches = list(batched(unembedded_art, batch_size))

    process_args = [(batch, retrieval_batch_size, embedding_batch_size) for batch in batches]

    with Pool(NUM_PROCS) as pool:
        pool.map(process_batch, process_args)

    end = time.time()
    logger.info(f"Total processing time: {end - start} seconds, to process {len(unembedded_art)} embeddings.")
