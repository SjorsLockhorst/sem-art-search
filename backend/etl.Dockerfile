FROM sjorslockhorst/sem-art-search

RUN poetry install --no-root --with etl

CMD ["python", "-m", "backend.etl.embed.main"]
