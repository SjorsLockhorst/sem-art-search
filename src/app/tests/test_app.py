from fastapi.testclient import TestClient

from ...app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    response.json() == "ok"


def test_art_query():
    oopjen_id = "nl-SK-C-1768"

    response = client.get(
        "/query",
        params={
            "art_query": "A portrait of a woman dressed in black, painted bij Rembrandt",
            "top_k": 1,
        },
    )
    assert response.status_code == 200
    art_objects = response.json()

    assert len(art_objects) == 1
    assert art_objects[0]["original_id"] == oopjen_id
