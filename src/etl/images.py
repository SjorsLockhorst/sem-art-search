import asyncio
from io import BytesIO

import httpx
from PIL import Image

from src.db.crud import retrieve_batch_art_objects


async def download_img(
    client: httpx.AsyncClient, id, url
) -> tuple[int, Image.Image] | None:
    response = await client.get(url)
    if response.status_code != 200:
        print(f"Error fetching image for art object {id}, skipping image")
        return None
    try:
        image = Image.open(BytesIO(response.content))
        return (id, image)
    except Exception as e:
        print(f"Error processing image for art object {id}: {e}")
        return None


async def get_images(count: int, batch_size: int) -> list[tuple[int, Image.Image]]:
    step_size = count // batch_size
    images: list[tuple[int, Image.Image]] = []
    async with httpx.AsyncClient() as client:
        for i in range(step_size):
            art_objects = retrieve_batch_art_objects(batch_size, i * batch_size)
            tasks = [
                download_img(client, art_object.id, art_object.image_url)
                for art_object in art_objects
            ]
            batch_images = await asyncio.gather(*tasks)
            images.extend([img for img in batch_images if img is not None])
    return images
