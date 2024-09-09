FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime

RUN apt update

RUN apt upgrade -y

RUN pip install --upgrade pip

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app/backend

# Copy only the pyproject.toml and poetry.lock to install dependencies
COPY ./backend/pyproject.toml ./backend/poetry.lock* /app/backend/

ENV VIRTUAL_ENV=art-env
RUN python -m venv $VIRTUAL_ENV --system-site-packages
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN poetry install --no-root --with etl

RUN apt install nvtop htop -y

COPY ./backend /app/backend

CMD ["python", "-m", "etl.embed"]
