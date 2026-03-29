FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

# Copy path dependencies first (relative to build context = repo root)
COPY services/shared /shared
COPY services/crudx /crudx

# Copy service source
COPY services/crud /app

RUN poetry install --no-root

ENV PYTHONPATH=/app/src

CMD ["poetry", "run", "uvicorn", "infrastructure.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
