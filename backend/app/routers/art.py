import numpy as np
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from db.crud import retrieve_best_image_match_w_embedding, retrieve_embedding_by_id
from db.models import ArtObjectsWithCoord, ArtQueryWithCoordsResponse
from etl.dim_reduc import get_embedding_coordinates, load_pca
from etl.embed.models import TextEmbedder

router = APIRouter()

text_embedder = TextEmbedder(device="cpu")

pca = load_pca()


@router.get("/query", tags=["art"])
def get_query_nearest_neighbors(art_query: str, top_k: int) -> ArtQueryWithCoordsResponse:
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
def get_image_nearest_neighbors(id: int, top_k: int) -> ArtQueryWithCoordsResponse:
    """
    Get's nearest neighbor images based on given test `query`.
    """
    embeds = retrieve_embedding_by_id(id)
    if not embeds:
        raise HTTPException(status_code=404, detail="No art objects found")

    # Need to reshape our embeddings since we only have 1 embedding

    embedding = embeds.image

    art_objects_embeddings = retrieve_best_image_match_w_embedding(embedding, top_k)

    if not art_objects_embeddings:
        raise HTTPException(status_code=404, detail="No art objects found")

    # Function returns many, we passed only 1 so we only get back 1, at index 0
    query_x, query_y = get_embedding_coordinates(pca, embedding.reshape(1, -1))[0]

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

    return ArtQueryWithCoordsResponse(query_x=query_x, query_y=query_y, art_objects_with_coords=close_images)
