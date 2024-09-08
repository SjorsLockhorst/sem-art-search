FROM sjorslockhorst/sem-art-search

RUN poetry install --no-root --with backend

EXPOSE 8000

# Ensure the start.sh script is executable
RUN chmod +x /app/backend/start.sh

# Use the start.sh script as the container's entry point
CMD ["/app/backend/start.sh"]
