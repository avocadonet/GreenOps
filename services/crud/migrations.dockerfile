FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY ../shared /shared
COPY ../crudx /crudx
COPY . .

RUN poetry install --no-root

ENV PYTHONPATH=/app/src

# Run migrations from the shared package (alembic.ini lives there)
CMD ["poetry", "run", "alembic", "--config", "/shared/alembic.ini", "upgrade", "head"]
