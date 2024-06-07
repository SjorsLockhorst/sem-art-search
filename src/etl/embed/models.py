import torch
from PIL import Image
from transformers import AutoProcessor, CLIPModel

from src.etl.errors import EmbeddingError
from src.etl.embed.config import HF_BASE_URL

class ArtEmbedder:

    @staticmethod
    def _get_device() -> str:
        """
        Return the device to be used (CUDA if available, otherwise CPU).
        """
        return "cuda" if torch.cuda.is_available() else "cpu"

    def norm(self, embeddings: torch.Tensor) -> torch.Tensor:
            return embeddings / embeddings.norm(p=2, dim=-1, keepdim=True)


class ImageEmbedder(ArtEmbedder):
    def __init__(self, hf_base_url: str = HF_BASE_URL):
        """
        Initialize the ImageEmbedder with the given Hugging Face base URL.
        """
        self.device = self._get_device()
        self.processor = AutoProcessor.from_pretrained(hf_base_url)
        self.model = CLIPModel.from_pretrained(hf_base_url)
        self.model.to(self.device)


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
            image_embeds = self._embed(inputs)
            return self.norm(image_embeds)

        except Exception as e:
            raise EmbeddingError(msg=str(e))

class TextEmbedder(ArtEmbedder):
    def __init__(self, hf_base_url: str = HF_BASE_URL):
        """
        Initialize the TextEmbedder with the given Hugging Face base URL.
        """
        self.device = self._get_device()
        self.processor = AutoProcessor.from_pretrained(hf_base_url)
        self.model = CLIPModel.from_pretrained(hf_base_url)
        self.model.to(self.device)


    def _process(self, texts: str | list[str]) -> torch.Tensor:
        """
        Process the input texts to prepare them for embedding.
        """
        return self.processor(text=texts, return_tensors="pt", padding=True)

    def _embed(self, inputs: torch.Tensor) -> torch.Tensor:
        """
        Generate embeddings for the processed texts.
        """
        return self.model.get_text_features(**inputs)

    def __call__(self, texts: str | list[str]) -> torch.Tensor:
        """
        Call the ImageEmbedder with a list of images to get their embeddings.
        """
        try:
            inputs = self._process(texts)
            inputs.to(self.device)
            image_embeds = self._embed(inputs)
            return self.norm(image_embeds)

        except Exception as e:
            raise EmbeddingError(msg=str(e))
