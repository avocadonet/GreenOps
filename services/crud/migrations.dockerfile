FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

# Copy path dependencies first (relative to build context = repo root)
COPY services/shared /shared
COPY services/crudx /crudx

# Copy service source (poetry.toml lives here)
COPY services/crud /app

RUN poetry install --no-root

# alembic.ini lives in /shared; PYTHONPATH exposes the shared package to env.py
ENV PYTHONPATH=/app/src:/shared/src

CMD ["poetry", "run", "alembic", "--config", "/shared/alembic.ini", "upgrade", "head"]
