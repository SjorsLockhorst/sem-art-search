# Use an official Python runtime as a parent image
FROM python:3.12

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app/backend

# Copy only the pyproject.toml and poetry.lock to install dependencies
COPY ./backend/pyproject.toml ./backend/poetry.lock* /app/backend/

# Install project dependencies
RUN poetry install --no-root 

# Copy the rest of the application code to the container, including the existing start.sh script
COPY ./backend /app/backend

# Run file which just creates models, downloading them to ./backend/.huggingface for cache
RUN poetry run python -m etl.embed.models

# Copy HF model files into the app
COPY ./backend/.huggingface /app/backend/.huggingface
