import asyncio
from itertools import batched

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


async def run_embed_stage(image_count: int, batch_size: int):
    """
    Main function to retrieve, embed, and store images in batches.

    Args:
    ----
        image_count (int): The total number of images to retrieve.
        batch_size (int): The number of images to retrieve per batch.

    """
    try:
        image_embedder = ImageEmbedder()
        task_queue: asyncio.Queue = asyncio.Queue()
        id_url_pairs = retrieve_unembedded_image_art(image_count)

        if not id_url_pairs:
            logger.info("No unembedded images, exiting.")
            return

        async with httpx.AsyncClient() as client:

            async def producer():
                n = image_count // batch_size
                for batch_id, id_url_batch in enumerate(batched(id_url_pairs, batch_size)):
                    logger.info(f"Starting to fetch {batch_size} new images. Progress: ({batch_id}/{n})")
                    ids_and_images = await fetch_images_from_pairs(client, id_url_batch)
                    if ids_and_images:
                        await task_queue.put(ids_and_images)
                    else:
                        logger.debug("No images retrived in batch, skipped entire batch")

                    logger.info(f"Done fetching {batch_size} images. Batch id: {batch_id}")

                # Sentinel value to indicate completion
                await task_queue.put(None)

            async def consumer():
                embed_batch_id = 0
                while True:
                    ids_and_images = await task_queue.get()
                    if ids_and_images is None:
                        break

                    logger.info(f"Starting to embed batch id: {embed_batch_id}")
                    ids_and_embeddings = get_images_embeddings(ids_and_images, image_embedder)
                    insert_batch_image_embeddings(ids_and_embeddings)
                    logger.info(f"Done embedding batch id: {embed_batch_id}")
                    embed_batch_id += 1

            await asyncio.gather(producer(), consumer())

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
    asyncio.run(run_embed_stage(image_count=count, batch_size=batch_size))
