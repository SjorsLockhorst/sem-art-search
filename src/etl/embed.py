from typing import Tuple, List

import requests
from PIL import Image
from transformers import AutoProcessor, CLIPModel
import torch

HF_BASE_URL = "openai/clip-vit-base-patch16"

def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


class ArtEmbedder():
    def __init__(self, hf_base_url: str = HF_BASE_URL):
        self.device = get_device()
        self.processor = AutoProcessor.from_pretrained(hf_base_url)
        self.model = CLIPModel.from_pretrained(hf_base_url)
        self.model.to(self.device)

    def process(self, images: Image | List[Image]):
        return self.processor(images=images, return_tensors="pt")
    
    def embed(self, inputs: torch.Tensor):
        return self.model.get_image_features(**inputs)

    def __call__(self, images: Image | List[Image]):
        inputs = self.process(images)
        inputs.to(self.device)
        return self.embed(inputs)



def get_img(url: str) -> Image:
    return Image.open(requests.get(url, stream=True).raw)


if __name__ == "__main__":
    TEST_IMG = "https://lh3.googleusercontent.com/J-mxAE7CPu-DXIOx4QKBtb0GC4ud37da1QK7CzbTIDswmvZHXhLm4Tv2-1H3iBXJWAW_bHm7dMl3j5wv_XiWAg55VOM=s0"
    img = get_img(TEST_IMG)
    art_embedder = ArtEmbedder()
    print(art_embedder([img]))

