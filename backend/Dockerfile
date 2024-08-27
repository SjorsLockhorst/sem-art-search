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

# Copy the rest of the application code to the container
COPY ./backend /app/backend

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run FastAPI with hot reloading when the container launches
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
