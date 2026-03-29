import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from infrastructure.providers.container import create_container
from infrastructure.scheduler.jobs import register_jobs

logging.basicConfig(level=logging.INFO)


async def main():
    container = create_container()
    scheduler = AsyncIOScheduler()
    register_jobs(scheduler, container)
    scheduler.start()
    try:
        await asyncio.Event().wait()  # run forever
    finally:
        scheduler.shutdown()
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
