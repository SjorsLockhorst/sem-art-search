import argparse

from PIL import Image
import requests

from src.etl.embed.embed import embed_text
from src.db.crud import retrieve_best_image_match

HF_BASE_URL = "openai/clip-vit-base-patch16"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find most simliar art work based on semantic similarity between "
        "user query, and image embeddings."
    )

    parser.add_argument(
        "query", type=str, help="The search query to find art works with."
    )

    parser.add_argument(
        "--top_k",
        type=int,
        default=1,
        help="The amount of most similar images to show.",
    )
    args = parser.parse_args()

    embedding = embed_text(args.query)
    art_objects = retrieve_best_image_match(embedding, args.top_k)

    image = Image.open(requests.get(art_objects[0].image_url, stream=True).raw)
    image.show()
