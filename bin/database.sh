#!/bin/bash

docker run -p 5432:5432 --name pgvector -e POSTGRES_PASSWORD=mysecretpassword -d pgvector/pgvector:pg16
