import asyncio
import itertools
import threading
import queue
import time

import httpx
import numpy as np
import torch
from loguru import logger
from PIL import Image
from sqlalchemy import exc

from db.crud import insert_batch_image_embeddings, retrieve_unembedded_image_art
from etl.embed.models import ImageEmbedder, TextEmbedder
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
    embeddings = image_embedder(list(imgs))

    if len(ids) != len(embeddings):
        raise EmbeddingError(msg="Amount of IDs does not match amount of embeddings")

    return list(zip(ids, embeddings, strict=False))


def embed_text(query: str) -> np.ndarray:
    embedder = TextEmbedder()
    return embedder(query)[0].cpu().detach().numpy()

def run_embed_stage(image_embedder: ImageEmbedder, image_count: int, batch_size: int):
    """
    Main function to retrieve, embed, and store images in batches.

    Args:
    ----
        image_count (int): The total number of images to retrieve.
        batch_size (int): The number of images to retrieve per batch.

    """
    try:
        task_queue: queue.Queue = queue.Queue()
        id_url_pairs = retrieve_unembedded_image_art(image_count)

        if not id_url_pairs:
            logger.info("No unembedded images, exiting.")
            return

        # Event to signal termination
        terminate_flag = threading.Event()

        def run_async_in_thread(coro):
            """Function to run async coroutines synchronously within a thread."""
            asyncio.run(coro)

        def producer():
            async def async_produce():
                try:
                    n = len(id_url_pairs) // batch_size
                    async with httpx.AsyncClient() as client:
                        for batch_id, id_url_batch in enumerate(batched(id_url_pairs, batch_size)):
                            logger.info(f"Starting to fetch {batch_size} new images. Progress: ({batch_id}/{n})")

                            if terminate_flag.is_set():
                                logger.warning("Producer is exiting due to termination flag.")
                                break

                            ids_and_images = await fetch_images_from_pairs(client, id_url_batch)  # Async call

                            if ids_and_images:
                                task_queue.put(ids_and_images)
                            else:
                                logger.debug("No images retrieved in batch, skipped entire batch")

                            logger.info(f"Done fetching {batch_size} images. Batch id: {batch_id}")

                except Exception as e:
                    logger.error(f"Async producer encountered an error: {e}")
                    terminate_flag.set()

                # If everything is done and no errors occurred, signal completion
                terminate_flag.set()

            run_async_in_thread(async_produce())

        def consumer():
            embed_batch_id = 0

            while not terminate_flag.is_set():
                try:
                    ids_and_images = task_queue.get(timeout=1)

                    if ids_and_images is None:
                        logger.warning("Consumer received None, exiting.")
                        terminate_flag.set()
                        break

                    logger.info(f"Starting to embed batch id: {embed_batch_id}")

                    ids_and_embeddings = get_images_embeddings(ids_and_images, image_embedder)
                    insert_batch_image_embeddings(ids_and_embeddings)

                    logger.info(f"Done embedding batch id: {embed_batch_id}")
                    embed_batch_id += 1

                except queue.Empty:
                    # End loop if flag is set and queue is empty
                    if terminate_flag.is_set() and task_queue.empty():
                        break

                except Exception as e:
                    logger.error(f"Consumer encountered an error: {e}")
                    terminate_flag.set()
                    break

        producer_thread = threading.Thread(target=producer)
        consumer_thread = threading.Thread(target=consumer)

        # Start both threads
        producer_thread.start()
        consumer_thread.start()

        # Join both threads
        producer_thread.join()
        consumer_thread.join()

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
    count = 10000
    batch_size = 8
    image_embedder = ImageEmbedder()
    run_embed_stage(image_embedder, image_count=count, batch_size=batch_size)
