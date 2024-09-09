from time import time

import torch
from loguru import logger
from PIL import Image
from transformers import (
    CLIPImageProcessor,
    CLIPTextModelWithProjection,
    CLIPTokenizerFast,
    AutoTokenizer,
    CLIPVisionModelWithProjection,
)
from multilingual_clip import pt_multilingual_clip

from etl.constants import HF_CACHE_DIR
from etl.embed.config import HF_IMG_BASE_URL, HF_TEXT_BASE_URL
from etl.errors import EmbeddingError



class ArtEmbedder:
    def __init__(self, device: str | None = None):
        if not device:
            self.device = self._get_cuda_if_available()
        else:
            self.device = device

    @staticmethod
    def _get_cuda_if_available() -> str:
        """
        Return the device to be used (CUDA if available, otherwise CPU).
        """
        return "cuda" if torch.cuda.is_available() else "cpu"

    def norm(self, embeddings: torch.Tensor) -> torch.Tensor:
        return embeddings / embeddings.norm(p=2, dim=-1, keepdim=True)


class ImageEmbedder(ArtEmbedder):
    def __init__(self, device: str | None = None, hf_base_url: str = HF_IMG_BASE_URL):
        """
        Initialize the ImageEmbedder with the given Hugging Face base URL.
        """
        super().__init__(device)

        self.processor = CLIPImageProcessor.from_pretrained(
            hf_base_url, cache_dir=HF_CACHE_DIR)
        self.model = CLIPVisionModelWithProjection.from_pretrained(
            hf_base_url, cache_dir=HF_CACHE_DIR)
        self.model.to(self.device)
        logger.info(f"Using ImageEmbedder with device {self.device}")

    def _process(self, images: Image.Image | list[Image.Image]) -> torch.Tensor:
        """
        Process the input images to prepare them for embedding.
        """
        tensor = self.processor(images, return_tensors="pt")
        return tensor

    def _embed(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Generate embeddings for the processed images.
        """
        return self.model(**inputs).image_embeds

    def __call__(self, images: Image.Image | list[Image.Image]) -> torch.Tensor:
        """
        Call the ImageEmbedder with a list of images to get their embeddings.
        """
        try:
            batch_size = 1 if isinstance(images, Image.Image) else len(images)
            logger.info(f"Embedding {batch_size} images")
            start_time = time()

            inputs = self._process(images)
            inputs.to(self.device)
            image_embeds = self._embed(inputs)
            proj_embeddings = self.norm(image_embeds)
            logger.info(
                f"Finished embedding texts in {time() - start_time} seconds.")
            return proj_embeddings

        except Exception as e:
            raise EmbeddingError(msg=str(e))


class TextEmbedder(ArtEmbedder):
    def __init__(self, device: str | None = None, hf_base_url: str = HF_TEXT_BASE_URL):
        """
        Initialize the TextEmbedder with the given Hugging Face base URL.
        """
        super().__init__()

        self.tokenizer = CLIPTokenizerFast.from_pretrained(
            hf_base_url, cache_dir=HF_CACHE_DIR)
        self.model = CLIPTextModelWithProjection.from_pretrained(
            hf_base_url, cache_dir=HF_CACHE_DIR)

        self.model.to(self.device)
        logger.info(f"Using TextEmbedder with device {self.device}")

    def _tokenize(self, texts: str | list[str]) -> torch.Tensor:
        """
        Process the input texts to prepare them for embedding.
        """
        return self.tokenizer(texts, return_tensors="pt", padding=True)

    def _embed(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Generate embeddings for the processed texts.
        """
        return self.model(**inputs).text_embeds

    def __call__(self, texts: str | list[str]) -> torch.Tensor:
        """
        Call the ImageEmbedder with a list of images to get their embeddings.
        """
        try:
            batch_size = 1 if isinstance(texts, str) else len(texts)
            logger.info(f"Embedding {batch_size} texts")
            start_time = time()

            inputs = self._tokenize(texts)
            inputs.to(self.device)
            text_embeds = self._embed(inputs)
            proj_embeddings = self.norm(text_embeds)
            logger.info(
                f"Finished embedding texts in {time() - start_time} seconds.")
            return proj_embeddings

        except Exception as e:
            raise EmbeddingError(msg=str(e))


class BilingualTextEmbedder(ArtEmbedder):
    def __init__(self, device: str | None = None, hf_base_url: str = HF_TEXT_BASE_URL):
        """
        Initialize the TextEmbedder with the given Hugging Face base URL.
        """

        logger.info(f"Using Huggingface cache dir {HF_CACHE_DIR}")

        logger.info("Init has been hit")
        super().__init__()
        logger.info("Post super init has been hit")

        self.model = pt_multilingual_clip.MultilingualCLIP.from_pretrained(
            hf_base_url, cache_dir=HF_CACHE_DIR)
        logger.info("Post multilingual clip has been hit")
        self.tokenizer = AutoTokenizer.from_pretrained(
            hf_base_url, cache_dir=HF_CACHE_DIR)

        self.model.to(self.device)

        logger.info(f"Using BilingualTextEmbedder with device {self.device}")

    def __call__(self, texts: str | list[str]) -> torch.Tensor:
        """
        Call the ImageEmbedder with a list of images to get their embeddings.
        """
        try:
            batch_size = 1 if isinstance(texts, str) else len(texts)
            logger.info(f"Embedding {batch_size} texts")
            start_time = time()

            text_embeds = self.model.forward(texts, self.tokenizer)
            proj_embeddings = self.norm(text_embeds)
            logger.info(
                f"Finished embedding texts in {time() - start_time} seconds.")
            return proj_embeddings

        except Exception as e:
            raise EmbeddingError(msg=str(e))

def get_image_embedder() -> ImageEmbedder:
    return ImageEmbedder()

def get_text_embedder(device: str | None = None) -> BilingualTextEmbedder | TextEmbedder:
    if HF_TEXT_BASE_URL == "M-CLIP/XLM-Roberta-Large-Vit-B-32":
        logger.info("Using BilingualTextEmbedder")
        return BilingualTextEmbedder(device=device)
    return TextEmbedder(device=device)



if __name__ == "__main__":
    # To be able to on demand pre download the models
    BilingualTextEmbedder(device="cpu")(["test"])
    # ImageEmbedder()
