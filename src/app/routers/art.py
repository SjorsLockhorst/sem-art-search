from fastapi import APIRouter

from src.db.crud import retrieve_best_image_match
from src.etl.embed.models import TextEmbedder
from src.db.models import ArtObjects

router = APIRouter()

text_embedder = TextEmbedder()

@router.get("/query", tags=["art"])
def get_image_and_neighbors(art_query: str, top_k: int) -> list[ArtObjects]:
    embedding = text_embedder(art_query)[0]
    art_objects = retrieve_best_image_match(embedding, top_k)
    return art_objects
