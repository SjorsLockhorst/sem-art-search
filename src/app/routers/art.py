from fastapi import APIRouter
import numpy as np

from src.db.crud import retrieve_best_image_match_w_embedding
from src.etl.embed.models import TextEmbedder
from src.db.models import ArtObjects, ArtObjectsWithCoord, ArtQueryWithCoordsResponse
from src.etl.dim_reduc import load_pca, get_embedding_coordinates

router = APIRouter()

text_embedder = TextEmbedder(device="cpu")

pca = load_pca()


@router.get("/query", tags=["art"])
def get_image_and_neighbors(art_query: str, top_k: int) -> ArtQueryWithCoordsResponse:
    text_embedding = text_embedder(art_query)[0].cpu().detach().numpy()

    art_objects_embeddings = retrieve_best_image_match_w_embedding(
        text_embedding, top_k
    )
    query_x, query_y = get_embedding_coordinates(
        pca, text_embedding.reshape(1, -1))[0]

    img_embeddings = []
    art_objects = []

    for art_object, img_embedding in art_objects_embeddings:
        img_embeddings.append(img_embedding)
        art_objects.append(art_object)

    all_img_embeddings = np.stack(img_embeddings)
    coordinates = get_embedding_coordinates(pca, all_img_embeddings)

    art_objs_with_coords = []
    for art_object, coords in zip(art_objects, coordinates):
        x, y = coords
        art_objs_with_coords.append(
            ArtObjectsWithCoord.from_art_object(art_object, x.item(), y.item())
        )

    return ArtQueryWithCoordsResponse(query_x=query_x, query_y=query_y, art_objects_with_coords=art_objs_with_coords)
