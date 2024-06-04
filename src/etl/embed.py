import asyncio
import logging

import torch
from PIL import Image
from transformers import AutoProcessor, CLIPModel

from src.db.crud import insert_batch_image_embeddings
from src.etl.images import get_images

HF_BASE_URL = "openai/clip-vit-base-patch16"


class ArtEmbedder:
    def __init__(self, hf_base_url: str = HF_BASE_URL):
        self.device = self.get_device()
        self.processor = AutoProcessor.from_pretrained(hf_base_url)
        self.model = CLIPModel.from_pretrained(hf_base_url)
        self.model.to(self.device)

    @classmethod
    def get_device(cls) -> str:
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _process(self, images: Image.Image | list[Image.Image]):
        return self.processor(images=images, return_tensors="pt")

    def _embed(self, inputs: torch.Tensor):
        return self.model.get_image_features(**inputs)

    def __call__(
        self, images: tuple[int, Image.Image] | list[tuple[int, Image.Image]]
    ) -> list[tuple[int, torch.Tensor]]:
        if isinstance(images, tuple):
            images = [images]

        ids, imgs = zip(*images)
        inputs = self._process(list(imgs))
        inputs.to(self.device)
        embeddings = self._embed(inputs)
        return list(zip(ids, embeddings))


async def main():
    try:
        # Adjust the count and batch_size according to system capabilities
        images = await get_images(count=10, batch_size=5)
        art_embedder = ArtEmbedder()
        embeddings = art_embedder(images)
        insert_batch_image_embeddings(embeddings)
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
