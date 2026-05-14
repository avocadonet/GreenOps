from dishka.integrations.faststream import setup_dishka
from faststream import FastStream
from faststream.nats import NatsBroker

from config import get_config
from container import create_container
from nats_consumers import router


def create_app() -> FastStream:
    config = get_config()
    broker = NatsBroker(config.nats_url)
    broker.include_router(router)

    app = FastStream(broker)
    container = create_container(broker)
    setup_dishka(container, app)
    return app
