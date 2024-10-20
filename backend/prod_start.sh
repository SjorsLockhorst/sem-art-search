#!/bin/sh

# Run the command to execute the Python file
python -m db.models

# Run FastAPI with hot reloading
exec fastapi run app/main.py --proxy-headers --host 0.0.0.0 --port 8000
