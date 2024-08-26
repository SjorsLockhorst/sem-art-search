import argparse
import asyncio

import httpx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import offsetbox

from db.crud import retrieve_best_image_match_w_embedding
from etl.dim_reduc import get_embedding_coordinates, load_pca
from etl.embed.embed import embed_text
from etl.images import download_img

HF_BASE_URL = "openai/clip-vit-base-patch16"


async def plot_images_with_coordinates(image_urls, coordinates, text_coordinates, text_query, zoom=0.07):
    async with httpx.AsyncClient() as client:
        tasks = [download_img(client, image_url) for image_url in image_urls]
        images = await asyncio.gather(*tasks)

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_title("Image Embeddings Visualization")

    for (x, y), image in zip(coordinates, images, strict=False):
        # Create an offset box for the image
        imagebox = offsetbox.AnnotationBbox(
            offsetbox.OffsetImage(image, zoom=zoom),  # Adjust zoom as needed
            (x, y),
            frameon=False,
        )
        ax.add_artist(imagebox)
    ax.scatter(text_coordinates[0], text_coordinates[1], color="red", s=100, label=text_query)
    ax.set_xlim(coordinates[:, 0].min() - 1, coordinates[:, 0].max() + 1)
    ax.set_ylim(coordinates[:, 1].min() - 1, coordinates[:, 1].max() + 1)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find most simliar art work based on semantic similarity between "
        "user query, and image embeddings."
    )

    parser.add_argument("query", type=str, help="The search query to find art works with.")

    parser.add_argument(
        "--top_k",
        type=int,
        default=1,
        help="The amount of most similar images to show.",
    )
    args = parser.parse_args()

    pca = load_pca()
    text_embedding = embed_text(args.query)
    art_objects_embeddings = retrieve_best_image_match_w_embedding(text_embedding, args.top_k)
    urls = [art_obj.image_url for art_obj, _ in art_objects_embeddings]
    all_embeddings = np.array([embedding for _, embedding in art_objects_embeddings])

    text_coordinate = get_embedding_coordinates(pca, text_embedding.reshape(1, -1))
    closest_image_coordinates = get_embedding_coordinates(pca, all_embeddings)
    print(f"Text coordinates: {text_coordinate[0]}")
    print(f"Image coordinates: \n{closest_image_coordinates}")

    asyncio.run(
        plot_images_with_coordinates(
            urls,
            closest_image_coordinates * args.top_k * 10,
            text_coordinate[0],
            args.query,
        )
    )