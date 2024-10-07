#!/bin/bash

# Start the database and backend services
sudo docker compose up -d database backend --build

# Wait until the database service is ready
until sudo docker compose --env-file=../.env exec database pg_isready -U ${POSTGRES_USER}; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up - executing ETL process"

# Run the ETL process
sudo docker compose run --rm backend sh -c "poetry run python -m etl.main" 
