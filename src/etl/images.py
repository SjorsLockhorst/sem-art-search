import asyncio
from loguru import logger
from io import BytesIO
from typing import List, Optional, Tuple

import httpx
from PIL import Image

async def download_img(
    client: httpx.AsyncClient, url: str
) -> Image.Image:
    """
    Download an image from the given URL using the provided HTTP client.

    Args:
        client (httpx.AsyncClient): The HTTP client to use for the request.
        id (int): The ID of the art object.
        url (str): The URL of the image to download.

    Returns:
        Optional[Tuple[int, Image.Image]]: A tuple containing the art object ID and the downloaded image, or None if the download or processing fails.
    """
    response = await client.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


async def download_img_w_id(
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
        image = await download_img(client, url)
        return (id, image)
    except httpx.HTTPStatusError:
        logger.error(f"Error fetching image for art object {id}, skipping image")
    except Exception as e:
        logger.error(f"Error processing image for art object {id}: {e}, skipping image")

    return None


async def fetch_images_from_pairs(
    client: httpx.AsyncClient, id_url_pairs: list[tuple[int, str]]
) -> List[Tuple[int, Image.Image]]:
    """
    Retrieve and download images.

    Args:
        client (httpx.AsyncClient): The HTTP client to use for the requests.
        id_url_pairs: list[tuple[int, str]]
            List of identifiers and image URLs.

    Returns:
        List[Tuple[int, Image.Image]]: A list of tuples containing IDs and their corresponding images.
    """
    images: List[Tuple[int, Image.Image]] = []

    tasks = [download_img_w_id(client, id, image_url) for id, image_url in id_url_pairs]
    batch_images = await asyncio.gather(*tasks)
    images.extend([img for img in batch_images if img is not None])

    return images
