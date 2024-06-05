import asyncio
import logging
from io import BytesIO
from typing import List, Optional, Tuple

import httpx
from PIL import Image

from src.db.crud import retrieve_batch_art_objects


async def download_img(
    client: httpx.AsyncClient, id: int, url: str
) -> Optional[Tuple[int, Image.Image]]:
    """
    Download an image from the given URL using the provided HTTP client.

    Args:
        client (httpx.AsyncClient): The HTTP client to use for the request.
        id (int): The ID of the art object.
        url (str): The URL of the image to download.

    Returns:
        Optional[Tuple[int, Image.Image]]: A tuple containing the art object ID and the downloaded image, or None if the download or processing fails.
    """
    try:
        response = await client.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return (id, image)
    except httpx.HTTPStatusError:
        logging.error(f"Error fetching image for art object {id}, skipping image")
    except Exception as e:
        logging.error(
            f"Error processing image for art object {id}: {e}, skipping image"
        )
    return None


async def get_ids_and_images(
    client: httpx.AsyncClient, batch_size: int, offset: int
) -> List[Tuple[int, Image.Image]]:
    """
    Retrieve and download images for a batch of art objects.

    Args:
        client (httpx.AsyncClient): The HTTP client to use for the requests.
        batch_size (int): The number of images to retrieve per batch.
        offset (int): The starting index for the batch.

    Returns:
        List[Tuple[int, Image.Image]]: A list of tuples containing art object IDs and their corresponding images.
    """
    images: List[Tuple[int, Image.Image]] = []
    art_objects = retrieve_batch_art_objects(batch_size, offset)
    tasks = [
        download_img(client, art_object.id, art_object.image_url)
        for art_object in art_objects
    ]
    batch_images = await asyncio.gather(*tasks)
    images.extend([img for img in batch_images if img is not None])

    return images
