FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HTTP_TIMEOUT=300

# Copy path dependencies first (relative to build context = repo root)
COPY services/shared /shared
COPY services/crudx /crudx

# Copy service source
COPY services/workers/pyproject.toml services/workers/poetry.lock* ./
COPY services/workers /app

RUN poetry lock && poetry install --no-root

ENV PYTHONPATH=/app/src

CMD ["poetry", "run", "python", "main.py"]
