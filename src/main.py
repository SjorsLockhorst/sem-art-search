import argparse

from PIL import Image
import requests
import numpy as np

from src.etl.embed.embed import embed_text
from src.db.crud import retrieve_best_image_match_w_embedding
from src.etl.dim_reduc import get_embedding_coordinates, load_pca

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

    pca = load_pca()
    text_embedding = embed_text(args.query)
    art_objects_embeddings = retrieve_best_image_match_w_embedding(
        text_embedding, args.top_k
    )
    all_embeddings = np.array([embedding for _, embedding in art_objects_embeddings])

    text_coordinate = get_embedding_coordinates(pca, text_embedding.reshape(1, -1))
    closest_image_coordinates = get_embedding_coordinates(pca, all_embeddings)
    print(f"Text coordinates: {text_coordinate[0]}")
    print(f"Image coordinates: \n{closest_image_coordinates}")
