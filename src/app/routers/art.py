from fastapi import APIRouter

from src.db.crud import retrieve_best_image_match
from src.etl.embed.embed import embed_text
from src.db.models import ArtObjects

router = APIRouter()


@router.get("/query", tags=["art"])
def get_image_and_neighbors(art_query: str, top_k: int) -> list[ArtObjects]:
    embedding = embed_text(art_query)
    art_objects = retrieve_best_image_match(embedding, top_k)
    return art_objects
