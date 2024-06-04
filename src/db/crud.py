import torch
from sqlmodel import Session, col, select

from src.db.models import ArtObjects, Embeddings, engine


def save_objects_to_database(art_objects: list[ArtObjects]):
    with Session(engine) as session:
        session.bulk_save_objects(art_objects)
        session.commit()


def insert_batch_image_embeddings(
    batch_embeddings: list[tuple[int, torch.Tensor]],
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

    with Session(engine) as session:
        embeddings = [
            Embeddings(art_object_id=art_object_id, image=embedding.cpu().numpy())
            for art_object_id, embedding in batch_embeddings
        ]
        session.bulk_save_objects(embeddings)
        session.commit()


def retrieve_batch_art_objects(batch_size: int, offset: int):
    """
    Retrieve a number of ArtObjects from the database, based on the batch_size

    Parameters
    ----------
    batch_size : int
        The number of ArtObjects to be retrieved in one call
    offset : int
        The number of rows to be skipped before fetching the objects

    """
    with Session(engine) as session:
        subquery = select(Embeddings.art_object_id)

        statement = (
            select(ArtObjects.id, ArtObjects.image_url)
            .where(col(ArtObjects.id).not_in(subquery))
            .offset(offset)
            .limit(batch_size)
            .order_by(col(ArtObjects.id).asc())
        )

        result = session.exec(statement)
        art_objects = result.all()

        return art_objects
