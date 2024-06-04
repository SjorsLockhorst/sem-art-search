import torch

from sqlmodel import Session
from src.models import engine, Embeddings

def insert_batch_image_embeddings(
    batch_art_object_ids: list[int], batch_embeddings: torch.Tensor
) -> None:
    """
    Insert a batch of embeddings.

    Parameters
    ----------
    batch_art_object_ids : list[int]
        Batch with ID of the corresponding ArtObject entries
    batch_embeddings: torch.Tensor[batch_size, 512]
        Batch with CLIP embeddings for each 

    Raises
    ------
    ValueError
        When length of batches of ID and embeddings is not equal.
    """
    if len(batch_art_object_ids) != len(batch_embeddings):
        raise ValueError("Batch size between id's and embeddings is not the same")

    with Session(engine) as session:
        embeddings = [
            Embeddings(art_object_id=art_object_id, image=embedding.cpu())
            for art_object_id, embedding in zip(batch_art_object_ids, batch_embeddings)
        ]
        session.bulk_save_objects(embeddings)
        session.commit()
