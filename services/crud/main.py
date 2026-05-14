import asyncio
import logging

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from infrastructure.providers.container import create_container
from infrastructure.scheduler.jobs import register_jobs

logging.basicConfig(level=logging.INFO)


async def main():
    container = create_container()
    scheduler = AsyncIOScheduler()
    register_jobs(scheduler, container)
    scheduler.start()

    config = uvicorn.Config(
        "infrastructure.api.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
    server = uvicorn.Server(config)
    try:
        await server.serve()
    finally:
        scheduler.shutdown()
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
