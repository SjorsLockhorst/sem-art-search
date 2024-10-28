#!/bin/sh

# TODO: Create another script for prod
poetry run python -m db.models

# Run FastAPI with hot reloading
exec poetry run fastapi dev --host 0.0.0.0 --port 8000 --reload
