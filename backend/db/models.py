from contextlib import contextmanager
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, SQLModel

from config import settings


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


class ArtQueryWithCoordsResponse(SQLModel, table=False):
    query_x: float
    query_y: float

    art_objects_with_coords: list[ArtObjectsWithCoord]


class Embeddings(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image: Any = Field(sa_column=Column(Vector(512)))
    art_object_id: int = Field(foreign_key="artobjects.id", unique=True)


engine = create_engine(settings.database_url)


def create_db_and_tables():
    with engine.connect() as con:
        con.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        con.commit()

    SQLModel.metadata.create_all(engine)

@contextmanager
def get_db_connection():
    # Make sure the connection/engine is only created within the process, to avoid SSL issues
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        session = local_session()
        yield session
    finally:
        session.close()

if __name__ == "__main__":
    create_db_and_tables()
