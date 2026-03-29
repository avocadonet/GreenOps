from dishka.integrations.faststream import setup_dishka
from faststream import FastStream
from faststream.kafka import KafkaBroker

from infrastructure.kafka.incident_consumer import router as incident_router
from infrastructure.kafka.telemetry_consumer import router as telemetry_router
from infrastructure.providers.container import create_container


def create_app(bootstrap_servers: str) -> FastStream:
    broker = KafkaBroker(bootstrap_servers)
    broker.include_router(telemetry_router)
    broker.include_router(incident_router)

    app = FastStream(broker)
    container = create_container(broker)
    setup_dishka(container, app)
    return app
