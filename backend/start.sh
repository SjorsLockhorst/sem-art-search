#!/bin/sh

# Run the command to execute the Python file
exec poetry run python -m db.models

# Run FastAPI with hot reloading
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
