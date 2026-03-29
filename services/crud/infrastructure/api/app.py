from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.configs import Config

from .exceptions_handlers import register_exceptions_handlers
from .router import v1_router


def create_app(container: AsyncContainer, config: Config) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exceptions_handlers(app)

    app.include_router(v1_router, prefix="/v1")
    setup_dishka(container, app)

    return app
