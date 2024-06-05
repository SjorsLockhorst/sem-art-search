import logging

import torch
from PIL import Image
from transformers import AutoProcessor, CLIPModel

from src.db.crud import insert_batch_image_embeddings
from src.etl.errors import EmbeddingError
from src.etl.images import get_ids_and_images

HF_BASE_URL = "openai/clip-vit-base-patch16"


class ImageEmbedder:
    def __init__(self, hf_base_url: str = HF_BASE_URL):
        """
        Initialize the ImageEmbedder with the given Hugging Face base URL.
        """
        self.device = self.get_device()
        self.processor = AutoProcessor.from_pretrained(hf_base_url)
        self.model = CLIPModel.from_pretrained(hf_base_url)
        self.model.to(self.device)

    @staticmethod
    def get_device() -> str:
        """
        Return the device to be used (CUDA if available, otherwise CPU).
        """
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _process(self, images: Image.Image | list[Image.Image]) -> torch.Tensor:
        """
        Process the input images to prepare them for embedding.
        """
        return self.processor(images=images, return_tensors="pt")

    def _embed(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Generate embeddings for the processed images.
        """
        return self.model.get_image_features(**inputs)

    def __call__(self, images: Image.Image | list[Image.Image]) -> torch.Tensor:
        """
        Call the ImageEmbedder with a list of images to get their embeddings.
        """
        try:
            inputs = self._process(images)
            inputs.to(self.device)
            return self._embed(inputs)
        except Exception as e:
            raise EmbeddingError(msg=str(e))


def get_images_embeddings(
    images: list[tuple[int, Image.Image]],
) -> list[tuple[int, torch.Tensor]]:
    """
    Generate embeddings for a list of images with their IDs.
    """
    ids, imgs = zip(*images)
    image_embedder = ImageEmbedder()
    embeddings = image_embedder(list(imgs))

    if len(ids) != len(embeddings):
        raise EmbeddingError(msg="Amount of IDs does not match amount of embeddings")

    return list(zip(ids, embeddings))


async def main():
    """
    Main function to retrieve, embed, and store images.
    """
    try:
        # Adjust the count and batch_size according to system capabilities
        ids_and_images = await get_ids_and_images(count=10, batch_size=5)
        ids_and_embeddings = get_images_embeddings(ids_and_images)
        insert_batch_image_embeddings(ids_and_embeddings)
        logging.info(f"Finished embedding of {len(ids_and_embeddings)} ArtObjects")
    except EmbeddingError as e:
        logging.error(f"Embedding Error: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise EmbeddingError(msg=str(e))
