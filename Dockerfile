# Use an official Python runtime as a parent image
# TODO: Make sure that start.sh script actually gives back correct SIGNAL
FROM python:3.12

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app/backend

# Copy only the pyproject.toml and poetry.lock to install dependencies
COPY ./backend/pyproject.toml ./backend/poetry.lock* /app/backend/

# Install project dependencies
RUN poetry install --no-root --extras "torch" --with backend

# Copy the rest of the application code to the container, including the existing start.sh script
COPY ./backend /app/backend

EXPOSE 8000

ENTRYPOINT ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port"," 8000"]