from fastapi.testclient import TestClient
from sqlmodel import Session, select
import numpy as np

from app.main import app
from db.models import Embeddings, engine
from etl.dim_reduc import load_pca, get_embedding_coordinates

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == "ok"


def test_art_query():
    oopjen_id = "nl-SK-C-1768"
    TOP_K = 10

    response = client.get(
        "/query",
        params={
            "art_query": "A portrait of a woman dressed in black, painted bij Rembrandt",
            "top_k": TOP_K,
        },
    )
    assert response.status_code == 200
    art_objects = response.json()

    assert len(art_objects) == TOP_K
    assert art_objects[0]["original_id"] == oopjen_id


# TODO: Remove this, integrate this somewhere useful to get coords automatically
def test_max_mean():
    with Session(engine) as session:
        statement = select(Embeddings.image)
        result = session.exec(statement)
        img_embeddings = result.all()

    all_embeddings = np.stack(img_embeddings)
    pca = load_pca()
    all_coords = get_embedding_coordinates(pca, all_embeddings)
    max_x = np.max(all_coords[:, 0])
    min_x = np.min(all_coords[:, 0])
    max_y = np.max(all_coords[:, 1])
    min_y = np.min(all_coords[:, 1])
    # print(max_x, min_x)
    # print(max_y, min_y)
    #
    # assert False
