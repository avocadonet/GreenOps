from dishka.integrations.faststream import setup_dishka
from faststream import FastStream
from faststream.kafka import KafkaBroker

from config import get_config
from container import create_container
from kafka_consumers import router


def create_app() -> FastStream:
    config = get_config()
    broker = KafkaBroker(config.kafka_bootstrap_servers)
    broker.include_router(router)

    app = FastStream(broker)
    container = create_container(broker)
    setup_dishka(container, app)
    return app
