from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, create_engine, text
from sqlmodel import Field, SQLModel


class ArtObjects(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_id: str = Field(index=True)
    image_url: str
    long_title: str
    artist: str


class ArtObjectsWithCoord(ArtObjects, table=False):
    x: float
    y: float

    @classmethod
    def from_art_object(cls, art_object: ArtObjects, x: float, y: float):
        return cls(
            id=art_object.id,
            original_id=art_object.original_id,
            image_url=art_object.image_url,
            long_title=art_object.long_title,
            artist=art_object.artist,
            x=x,
            y=y,
        )


class Embeddings(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image: Any = Field(sa_column=Column(Vector(512)))
    art_object_id: int = Field(foreign_key="artobjects.id", unique=True)


engine = create_engine("postgresql+psycopg2://postgres:mysecretpassword@localhost:5432")


def create_db_and_tables():
    with engine.connect() as con:
        con.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        con.commit()

    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
