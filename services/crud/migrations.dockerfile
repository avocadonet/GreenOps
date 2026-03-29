FROM python:3.12-slim

RUN pip3 install poetry

WORKDIR /app

COPY ./services/crud/pyproject.toml ./crud/pyproject.toml
COPY ./services/crud/poetry.lock ./crud/poetry.lock
COPY ./services/crudx ./crudx

WORKDIR /app/crudx
RUN poetry build

WORKDIR /app/crud
RUN poetry install --no-root

WORKDIR /app
COPY ./services/crud ./crud

WORKDIR /app/crud
CMD poetry run alembic upgrade head
