#!/bin/bash
# Tests running the serverless worker with GPU support, mounts in huggingface dir so doesn't need to redownload weights.
sudo docker run -it --rm --gpus=all --env-file=.env -v $PWD/../.huggingface:/app/.huggingface sjorslockhorst/sem-art-search-etl:latest poetry run python -m etl.infra.embed_handler
