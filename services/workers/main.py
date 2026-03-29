import asyncio

from infrastructure.kafka.app import create_app
from infrastructure.configs.config import get_config


async def main():
    config = get_config()
    app = create_app(config.kafka_bootstrap_servers)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
