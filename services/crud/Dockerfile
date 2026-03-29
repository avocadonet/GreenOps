FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY ../shared /shared
COPY ../crudx /crudx
COPY . .

RUN poetry install --no-root

ENV PYTHONPATH=/app/src

CMD ["poetry", "run", "uvicorn", "infrastructure.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
