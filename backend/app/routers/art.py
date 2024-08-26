import numpy as np
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from db.crud import retrieve_best_image_match_w_embedding
from db.models import ArtObjectsWithCoord, ArtQueryWithCoordsResponse
from etl.dim_reduc import get_embedding_coordinates, load_pca
from etl.embed.models import TextEmbedder

router = APIRouter()

text_embedder = TextEmbedder(device="cpu")

pca = load_pca()

# TODO: These shouldn't be hardcoded, test_app.py has code that finds these numbers
MAX_X = 0.41522586
MIN_X = -0.44345528

MAX_Y = 0.49789447
MIN_Y = -0.3281755


@router.get("/query", tags=["art"])
def get_image_and_neighbors(art_query: str, top_k: int) -> ArtQueryWithCoordsResponse:
    text_embedding = text_embedder(art_query)[0].cpu().detach().numpy()

    art_objects_embeddings = retrieve_best_image_match_w_embedding(text_embedding, top_k)

    if not art_objects_embeddings:
        raise HTTPException(status_code=404, detail="No art objects found")

    query_x, query_y = get_embedding_coordinates(pca, text_embedding.reshape(1, -1))[0]

    query_x = (query_x - MIN_X) / (MAX_X - MIN_X)
    query_y = (query_y - MIN_Y) / (MAX_Y - MIN_Y)

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
        art_objs_with_coords.append(ArtObjectsWithCoord.from_art_object(art_object, x.item(), y.item()))

    return ArtQueryWithCoordsResponse(query_x=query_x, query_y=query_y, art_objects_with_coords=art_objs_with_coords)
