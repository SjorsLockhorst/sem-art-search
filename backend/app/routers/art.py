from typing import Annotated

import numpy as np
from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from pydantic import Field, PositiveInt

from db.crud import retrieve_best_image_match_w_embedding, retrieve_closest_to_artobject
from db.models import ArtObjectsWithCoord, ArtQueryWithCoordsResponse
from etl.dim_reduc import get_embedding_coordinates, load_pca
from etl.embed.models import TextEmbedder

# Added comment for test
router = APIRouter()

text_embedder = TextEmbedder(device="cpu")

pca = load_pca()

TopK = Annotated[int, Query(ge=1, le=15)]


@router.get("/query", tags=["art"])
def get_query_nearest_neighbors(art_query: Annotated[str, Query(max_length=250)], top_k: TopK) -> ArtQueryWithCoordsResponse:
    """
    Get's nearest neighbor images based on given test `query`.
    """
    text_embedding = text_embedder(art_query)[0].cpu().detach().numpy()

    art_objects_embeddings = retrieve_best_image_match_w_embedding(text_embedding, top_k)

    if not art_objects_embeddings:
        raise HTTPException(status_code=404, detail="No art objects found")

    query_x, query_y = get_embedding_coordinates(pca, text_embedding.reshape(1, -1))[0]

    img_embeddings = []
    art_objects = []

    for art_object, img_embedding in art_objects_embeddings:
        img_embeddings.append(img_embedding)
        art_objects.append(art_object)

    all_img_embeddings = np.stack(img_embeddings)
    coordinates = get_embedding_coordinates(pca, all_img_embeddings)

    art_objs_with_coords = []

    for art_object, coords in zip(art_objects, coordinates, strict=False):
        x, y = coords
        art_objs_with_coords.append(ArtObjectsWithCoord.from_art_object(art_object, x.item(), y.item()))

    return ArtQueryWithCoordsResponse(query_x=query_x, query_y=query_y, art_objects_with_coords=art_objs_with_coords)


@router.get("/image", tags=["art"])
def get_image_nearest_neighbors(idx: Annotated[int, Query(ge=1)], top_k: TopK) -> list[ArtObjectsWithCoord]:
    """
    Get's nearest neighbor images based on given test `query`.
    """
    art_objects_embeddings = retrieve_closest_to_artobject(idx, top_k)

    if not art_objects_embeddings:
        raise HTTPException(status_code=404, detail="No art objects found")

    img_embeddings = []
    art_objects = []

    for art_object, img_embedding in art_objects_embeddings:
        img_embeddings.append(img_embedding)
        art_objects.append(art_object)

    all_img_embeddings = np.stack(img_embeddings)
    coordinates = get_embedding_coordinates(pca, all_img_embeddings)

    close_images = []

    for art_object, coords in zip(art_objects, coordinates, strict=False):
        x, y = coords
        close_image = ArtObjectsWithCoord.from_art_object(art_object, x.item(), y.item())
        close_images.append(close_image)

    return close_images
