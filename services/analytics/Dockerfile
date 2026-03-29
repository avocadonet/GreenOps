FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

# Copy path dependencies first (relative to build context = repo root)
COPY services/shared /shared

# Copy service source
COPY services/analytics /app

RUN poetry install --no-root

ENV PYTHONPATH=/app/src

CMD ["poetry", "run", "python", "main.py"]
