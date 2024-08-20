from fastapi import APIRouter
import numpy as np

from src.db.crud import retrieve_best_image_match_w_embedding
from src.etl.embed.models import TextEmbedder
from src.db.models import ArtObjects, ArtObjectsWithCoord
from src.etl.dim_reduc import load_pca, get_embedding_coordinates

router = APIRouter()

text_embedder = TextEmbedder(device="cpu")

pca = load_pca()

# TODO: These shouldn't be hardcoded, test_app.py has code that finds these numbers
MAX_X = 0.41522586
MIN_X = -0.44345528

MAX_Y = 0.49789447
MIN_Y = -0.3281755


@router.get("/query", tags=["art"])
def get_image_and_neighbors(art_query: str, top_k: int) -> list[ArtObjectsWithCoord]:
    text_embedding = text_embedder(art_query)[0]
    art_objects_embeddings = retrieve_best_image_match_w_embedding(
        text_embedding.cpu().detach().numpy(), top_k
    )
    img_embeddings = []
    art_objects = []

    for art_object, img_embedding in art_objects_embeddings:
        img_embeddings.append(img_embedding)
        art_objects.append(art_object)

    all_img_embeddings = np.stack(img_embeddings)
    coordinates = get_embedding_coordinates(pca, all_img_embeddings)
    coordinates[:, 0] = (coordinates[:, 0] - MIN_X) / (MAX_X - MIN_X)
    coordinates[:, 1] = (coordinates[:, 1] - MIN_Y) / (MAX_Y - MIN_Y)

    art_objs_with_coords = []
    for art_object, coords in zip(art_objects, coordinates):
        x, y = coords
        art_objs_with_coords.append(
            ArtObjectsWithCoord.from_art_object(art_object, x.item(), y.item())
        )

    return art_objs_with_coords
