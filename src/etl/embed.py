from io import BytesIO
import httpx
from PIL import Image
from transformers import AutoProcessor, CLIPModel
import torch
from src.models import ArtObject, engine
from sqlmodel import Session, select
import asyncio

HF_BASE_URL = "openai/clip-vit-base-patch16"


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


class ArtEmbedder:
    def __init__(self, hf_base_url: str = HF_BASE_URL):
        self.device = get_device()
        self.processor = AutoProcessor.from_pretrained(hf_base_url)
        self.model = CLIPModel.from_pretrained(hf_base_url)
        self.model.to(self.device)

    def process(self, images: Image.Image | list[Image.Image]):
        return self.processor(images=images, return_tensors="pt")

    def embed(self, inputs: torch.Tensor):
        return self.model.get_image_features(**inputs)

    def __call__(self, images: Image.Image | list[Image.Image]):
        inputs = self.process(images)
        inputs.to(self.device)
        return self.embed(inputs)


async def download_img(client, url):
    response = await client.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


async def get_images(batch_size: int, offset: int) -> list[Image.Image]:
    """Function used to both fetch a number of images from the database
    and then use the retrieved image urls to download the actual images asynchronously

    Parameters
    ----------
    batch_size : int
        The number of images retrieved in one run
    offset : int
        The offset to prevent fetching the same image twice.
        If the batch size is 5, the offset needs to be incremented by 5 for each iteration to skip the correct images

    Returns
    -------
    list[Image.Image]
        A list of PIL images objects
    """
    with Session(engine) as session:
        statement = (
            select(ArtObject.original_id, ArtObject.image_url)
            .offset(offset)
            .limit(batch_size)
        )
        result = session.exec(statement)
        art_objects = result.all()
    async with httpx.AsyncClient() as client:
        tasks = [
            download_img(client, art_object.image_url) for art_object in art_objects
        ]
        images = await asyncio.gather(*tasks)
    return images


async def main():
    images = await get_images(batch_size=5, offset=0)
    art_embedder = ArtEmbedder()
    print(art_embedder(images))


if __name__ == "__main__":
    asyncio.run(main())
