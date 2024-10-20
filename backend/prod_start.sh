#!/bin/sh

# Run the command to execute the Python file
poetry run python -m db.models

# Run FastAPI with hot reloading
exec poetry run fastapi run app/main.py --proxy-headers --host 0.0.0.0 --port 8000 
