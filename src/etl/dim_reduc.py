import os
from typing import Optional

import numpy as np
from joblib import dump, load
from loguru import logger
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

from src import MODEL_DIR
from src.db.crud import retrieve_embeddings

SEED = 42
PCA_PATH = os.path.join(MODEL_DIR, "pca.joblib")


def fit_on_image_embeddings(limit: Optional[int] = None):
    logger.info("Starting to retrieve embeddings from DB.")
    embeddings = retrieve_embeddings(limit=limit)
    logger.info("Done retrieving embeddings")
    X = np.array([embedding.image for embedding in embeddings])

    logger.info("Starting to fit PCA model.")
    pca_pipeline = Pipeline([
        ("projection", PCA(n_components=2, random_state=SEED)),
        ("scaler", MinMaxScaler(feature_range=(0, 1)))
    ])
    pca_pipeline.fit(X) 
    coordinates = pca_pipeline.transform(X)
    logger.info("Done fitting PCA model!")
    return pca_pipeline, coordinates


def fit_pca_on_all():
    logger.info("Starting to fit TSNE model on all image embeddings in DB.")
    pca, _ = fit_on_image_embeddings()
    logger.info("Done fitting model.")
    logger.info(f"Saving model to {PCA_PATH}")
    dump(pca, PCA_PATH)
    logger.info("Done saving model!")


def load_pca() -> PCA:
    logger.info("Loading PCA model for transformation.")
    return load(PCA_PATH)


def get_embedding_coordinates(pca: PCA, embeddings: np.ndarray) -> np.ndarray:
    coordinates = pca.transform(embeddings)
    logger.info(
        f"Transformed from original shape {embeddings.shape} -> {coordinates.shape}"
    )
    return coordinates


if __name__ == "__main__":
    fit_pca_on_all()
