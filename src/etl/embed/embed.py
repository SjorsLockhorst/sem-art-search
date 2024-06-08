import asyncio
from loguru import logger
import httpx
import torch
from PIL import Image

from src.db.crud import insert_batch_image_embeddings
from src.etl.errors import EmbeddingError
from src.etl.images import get_ids_and_images
from src.etl.embed.models import ImageEmbedder, TextEmbedder


def get_images_embeddings(
    images: list[tuple[int, Image.Image]], image_embedder: ImageEmbedder
) -> list[tuple[int, torch.Tensor]]:
    """
    Generate embeddings for a list of images with their IDs.
    """
    ids, imgs = zip(*images)
    embeddings = image_embedder(list(imgs))

    if len(ids) != len(embeddings):
        raise EmbeddingError(
            msg="Amount of IDs does not match amount of embeddings")

    return list(zip(ids, embeddings))


def embed_text(query: str):
    embedder = TextEmbedder()
    return embedder(query)[0]


async def run_embed_stage(image_count: int, batch_size: int):
    """
    Main function to retrieve, embed, and store images in batches.

    Args:
        count (int): The total number of images to retrieve.
        batch_size (int): The number of images to retrieve per batch.
    """
    try:
        image_embedder = ImageEmbedder()
        async with httpx.AsyncClient() as client:
            for offset in range(0, image_count, batch_size):
                ids_and_images = await get_ids_and_images(client, batch_size, offset)
                ids_and_embeddings = get_images_embeddings(
                    ids_and_images, image_embedder
                )
                insert_batch_image_embeddings(ids_and_embeddings)
                logger.info(
                    f"Finished embedding of {len(ids_and_embeddings)} ArtObjects in batch starting at offset {offset}"
                )
    except EmbeddingError as e:
        logger.error(f"Embedding Error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise EmbeddingError(msg=str(e))




if __name__ == "__main__":
    count = 10
    batch_size = 5
    asyncio.run(run_embed_stage(image_count=count, batch_size=batch_size))
