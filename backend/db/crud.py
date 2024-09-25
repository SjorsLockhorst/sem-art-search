import numpy as np
import torch
from sqlalchemy import func
from sqlmodel import Session, col, exists, select

from db.models import ArtObjects, Embeddings, engine


def check_count_art_objects() -> int:
    with Session(engine) as session:
        count = session.exec(select(func.count()).select_from(ArtObjects)).first()
        return count if count else 0


def save_objects_to_database(art_objects: list[ArtObjects]):
    with Session(engine) as session:
        session.bulk_save_objects(art_objects)
        session.commit()


def insert_batch_image_embeddings(
        conn: Session, batch_embeddings: list[tuple[int, torch.Tensor]],
) -> None:
    """
    Insert a batch of embeddings.

    Parameters
    ----------
    batch_embeddings: list[tuple[int, torch.Tensor]]
        List of tuples, each containing the ID of the corresponding ArtObject and its CLIP embedding

    Raises
    ------
    ValueError
        When the list of embeddings is empty.

    """
    if not batch_embeddings:
        raise ValueError("The list of embeddings is empty")

    with conn as session:
        embeddings = [
            Embeddings(art_object_id=art_object_id, image=embedding.detach().cpu().numpy())
            for art_object_id, embedding in batch_embeddings
        ]
        session.bulk_save_objects(embeddings)
        session.commit()


def retrieve_unembedded_image_art(count: int, offset: int = 0):
    """
    Retrieve a number of ArtObjects from the database, based on the batch_size

    Parameters
    ----------
    count : int
        The number of ArtObjects to be retrieved in one call

    """
    with Session(engine) as session:
        statement = (
            select(ArtObjects.id, ArtObjects.image_url)
            .where(~exists(select(Embeddings.art_object_id).where(Embeddings.art_object_id == ArtObjects.id)))
            .limit(count)
            .order_by(col(ArtObjects.id).asc())
            .offset(offset)
        )

        result = session.exec(statement)
        art_objects = result.all()

        return art_objects


def retrieve_best_image_match(embedding: torch.Tensor, top_k: int) -> list[ArtObjects]:
    with Session(engine) as session:
        top_ids = session.exec(
            select(Embeddings.art_object_id)
            .order_by(Embeddings.image.cosine_distance(embedding.cpu().detach().numpy()))
            .limit(top_k)
        ).all()

        art_objects = session.exec(select(ArtObjects).where(col(ArtObjects.id).in_(top_ids))).all()

    return list(art_objects)


def retrieve_best_image_match_w_embedding(embedding: np.ndarray, top_k: int) -> list[tuple[ArtObjects, np.ndarray]]:
    with Session(engine) as session:
        joined_result = session.exec(
            select(ArtObjects, Embeddings.image)
            .order_by(Embeddings.image.cosine_distance(embedding))
            .limit(top_k)
            .join(ArtObjects)
        ).all()

    return list(joined_result)


def retrieve_embeddings(limit: int | None = None) -> list[Embeddings]:
    with Session(engine) as session:
        query = select(Embeddings)
        if limit:
            query = query.limit(limit)
        embeddings = session.exec(query).all()

    return list(embeddings)


def retrieve_embedding_by_id(id: int) -> Embeddings | None:
    with Session(engine) as session:
        return session.exec(select(Embeddings).where(Embeddings.art_object_id == id)).first()
