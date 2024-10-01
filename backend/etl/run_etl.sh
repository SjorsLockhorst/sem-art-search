#!/bin/bash

# Start the database and backend services
docker compose up -d database backend

# Wait until the database service is ready
until docker compose exec database pg_isready -U ${POSTGRES_USER}; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up - executing ETL process"

# Run the ETL process
docker compose run --rm backend sh -c "poetry run python -m etl.main" 
