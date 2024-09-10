import argparse
import asyncio
import itertools
import queue
import threading
import time

import httpx
import numpy as np
import torch
from loguru import logger
from PIL import Image
from sqlalchemy import exc
from torch.multiprocessing import Queue

from db.crud import insert_batch_image_embeddings, retrieve_unembedded_image_art
from etl.embed.models import ImageEmbedder, TextEmbedder, get_image_embedder
from etl.errors import EmbeddingError
from etl.images import fetch_images_from_pairs


def batched(iterable, n):
    """Return batches of size n from iterable."""
    it = iter(iterable)
    while batch := list(itertools.islice(it, n)):
        yield batch


def get_images_embeddings(
    images: list[tuple[int, Image.Image]], image_embedder: ImageEmbedder
) -> list[tuple[int, torch.Tensor]]:
    """
    Generate embeddings for a list of images with their IDs.
    """
    ids, imgs = zip(*images, strict=False)
    embeddings = image_embedder(list(imgs)).detach()

    if len(ids) != len(embeddings):
        raise EmbeddingError(
            msg="Amount of IDs does not match amount of embeddings")

    return list(zip(ids, embeddings, strict=False))


def embed_text(query: str) -> np.ndarray:
    embedder = TextEmbedder()
    return embedder(query)[0].cpu().detach().numpy()


def image_producer(id_url_pairs, batch_size, image_queue, terminate_flag, all_images_downloaded_flag):
    async def async_image_producer():
        try:
            n = len(id_url_pairs) // batch_size
            async with httpx.AsyncClient() as client:
                for batch_id, id_url_batch in enumerate(batched(id_url_pairs, batch_size)):
                    logger.info(
                        f"Starting to fetch {batch_size} new images. Progress: ({batch_id}/{n})")

                    if terminate_flag.is_set():
                        logger.warning(
                            "Producer is exiting due to termination flag.")
                        break

                    # Async call
                    ids_and_images = await fetch_images_from_pairs(client, id_url_batch)

                    if ids_and_images:
                        image_queue.put(ids_and_images)
                    else:
                        logger.debug(
                            "No images retrieved in batch, skipped entire batch")

                    logger.info(
                        f"Done fetching {batch_size} images. Batch id: {batch_id}")

        except Exception as e:
            logger.error(f"Async producer encountered an error: {e}")
            terminate_flag.set()
            raise

        all_images_downloaded_flag.set()

    # If everything is done and no errors occurred, signal completion
    asyncio.run(async_image_producer())


def image_consumer_embedding_producer(
    image_embedder: ImageEmbedder,
    image_queue: Queue,
    embedding_queue: Queue,
    terminate_flag: threading.Event,
    all_images_downloaded_flag: threading.Event,
    all_images_embedded_flag: threading.Event,
):
    embed_batch_id = 0

    while not terminate_flag.is_set():
        try:
            ids_and_images = image_queue.get(timeout=1)

            if ids_and_images is None:
                logger.warning("Consumer received None, exiting.")
                terminate_flag.set()
                break

            logger.info(f"Starting to embed batch id: {embed_batch_id}")

            ids_and_embeddings = get_images_embeddings(
                ids_and_images, image_embedder)
            embedding_queue.put(ids_and_embeddings)

            logger.info(f"Done embedding batch id: {embed_batch_id}")
            embed_batch_id += 1

        except queue.Empty:
            # End loop if flag is set and queue is empty
            if all_images_downloaded_flag.is_set():
                logger.info("Done embedding all images.")
                all_images_embedded_flag.set()
                break
            if terminate_flag.is_set():
                logger.error(
                    "Image embedder thread terminated by terminate flag.")
                break

        except Exception as e:
            logger.error(f"Image embedder thread encountered an error: {e}")
            terminate_flag.set()
            raise


def embedding_consumer_bulk_insert(
    embedding_queue, terminate_flag, all_images_embedded_flag, all_embeddings_saved_flag
):
    while not terminate_flag.is_set():
        try:
            ids_and_embeddings = embedding_queue.get(timeout=1)
            insert_batch_image_embeddings(ids_and_embeddings)
            logger.info(
                f"Done inserting {len(ids_and_embeddings)} embeddings into SQL database.")

        except queue.Empty:
            if all_images_embedded_flag.is_set():
                logger.info("Done storing all embeddings in the SQL database")
                all_embeddings_saved_flag.set()
                break

        except Exception as e:
            logger.error(
                f"Embedder SQL inserter thread encountered an error: {e}")
            terminate_flag.set()
            raise


def run_embed_stage(image_embedder: ImageEmbedder, image_count: int, batch_size: int, num_embed_threads: int):
    """
    Main function to retrieve, embed, and store images in batches.
    """
    try:
        # Queue to store downloaded images into
        image_queue= Queue()

        # Queue to store extracted embeddings in
        embedding_queue = Queue()

        # Retrieve from the database which ArtObjects don't have an Embedding
        id_url_pairs = retrieve_unembedded_image_art(image_count)

        # If there's None, we exist
        if not id_url_pairs:
            logger.info("No unembedded images, exiting.")
            return

        # Terminate flag in case something goes wrong, should exit all threads
        terminate_flag = threading.Event()

        # Once all images have been downloaded
        all_images_downloaded_flag = threading.Event()

        # Once all images have been embedded
        all_images_embedded_flag = threading.Event()

        # Once all images have been saved
        all_embeddings_saved_flag = threading.Event()

        image_prod_args = [id_url_pairs, batch_size, image_queue,
            terminate_flag, all_images_downloaded_flag]

        emb_prod_args = [
            image_embedder,
            image_queue,
            embedding_queue,
            terminate_flag,
            all_images_downloaded_flag,
            all_images_embedded_flag,
        ]

        emb_save_args = [embedding_queue, terminate_flag,
            all_images_embedded_flag, all_embeddings_saved_flag]

        image_producer_thread = threading.Thread(
            target=image_producer, args=image_prod_args)

        embed_threads = [threading.Thread(target=image_consumer_embedding_producer, args=emb_prod_args) for _ in range(num_embed_threads)]

        embedding_consumer_insert_thread = threading.Thread(target=embedding_consumer_bulk_insert, args=emb_save_args)

        image_producer_thread.start()

        for embed_thread in embed_threads:
            embed_thread.start()

        embedding_consumer_insert_thread.start()

        image_producer_thread.join()

        for embed_thread in embed_threads:
            embed_thread.join()

        embedding_consumer_insert_thread.join()

        logger.info("Processing completed.")

    except EmbeddingError as e:
        logger.error(f"Embedding Error: {e}")
        raise
    except exc.SQLAlchemyError as e:
        logger.error(f"Database Error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser(description="Run embedding stage")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size for embedding")
    parser.add_argument("--num-embed-threads", type=int, default=4, help="Amount of threads to use for embedding")
    parser.add_argument("--count", type=int, default=10000, help="Number of images to embed")
    args = parser.parse_args()
    image_embedder = get_image_embedder()
    run_embed_stage(
        image_embedder, image_count=args.count, batch_size=args.batch_size, num_embed_threads=args.num_embed_threads
    )
    end = time.time()
    logger.info(f"Elapsed: {end - start}")
