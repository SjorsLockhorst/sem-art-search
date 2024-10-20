import numpy as np
from joblib import dump, load
from loguru import logger
from sklearn.base import TransformerMixin
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from db.crud import retrieve_embeddings
from etl.constants import MODEL_DIR

SEED = 42
PCA_PATH = MODEL_DIR / "pca.joblib"


def build_projection_pipe(projection: TransformerMixin) -> Pipeline:
    return Pipeline([("projection", projection), ("scaler", MinMaxScaler(feature_range=(0, 1)))])


def fit_pca_on_image_embeddings(limit: int | None = None):
    logger.info("Starting to retrieve embeddings from DB.")
    embeddings = retrieve_embeddings(limit=limit)
    logger.info("Done retrieving embeddings")
    X = np.array([embedding.image for embedding in embeddings])

    logger.info("Starting to fit PCA model.")
    pca_pipeline = build_projection_pipe(PCA(n_components=2, random_state=SEED))
    pca_pipeline.fit(X)
    coordinates = pca_pipeline.transform(X)
    logger.info("Done fitting PCA model!")
    return pca_pipeline, coordinates


def fit_pca_on_all():
    logger.info("Starting to fit PCA model on all image embeddings in DB.")
    pca, _ = fit_pca_on_image_embeddings()
    logger.info("Done fitting model.")
    logger.info(f"Saving model to {PCA_PATH}")
    dump(pca, PCA_PATH)
    logger.info("Done saving model!")


def load_pca() -> PCA:
    logger.info("Loading PCA model for transformation.")
    return load(PCA_PATH)


def get_embedding_coordinates(pca: PCA, embeddings: np.ndarray) -> np.ndarray:
    coordinates = pca.transform(embeddings)
    logger.info(f"Transformed from original shape {embeddings.shape} -> {coordinates.shape}")
    return coordinates


if __name__ == "__main__":
    fit_pca_on_all()
