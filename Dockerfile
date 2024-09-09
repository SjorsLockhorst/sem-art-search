# Use an official Python runtime as a parent image
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

# Ensure the start.sh script is executable
RUN chmod +x /app/backend/start.sh

# Use the start.sh script as the container's entry point
CMD ["/app/backend/start.sh"]
