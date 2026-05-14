from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from infrastructure.api.exceptions_handlers import register_handlers
from infrastructure.api.router import include_routers
from infrastructure.providers.container import create_container


def create_app() -> FastAPI:
    app = FastAPI(title="GreenOps CRUD", version="0.1.0")
    container = create_container()
    setup_dishka(container, app)
    register_handlers(app)
    include_routers(app)
    Instrumentator().instrument(app).expose(app)
    return app
