import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dishka import AsyncContainer

from application.average_load.service import AverageLoadService
from application.energy_balance.service import EnergyBalanceService

logger = logging.getLogger(__name__)


def register_jobs(scheduler: AsyncIOScheduler, container: AsyncContainer) -> None:
    async def run_average_load():
        logger.info("Running hourly AverageLoad job")
        async with container() as request_container:
            service = await request_container.get(AverageLoadService)
            await service.run_hourly()

    async def run_energy_balance():
        logger.info("Running daily EnergyBalance job")
        async with container() as request_container:
            service = await request_container.get(EnergyBalanceService)
            await service.run_daily()

    # :05 past every hour — avoids the :00 thundering herd
    scheduler.add_job(run_average_load, CronTrigger(minute=5), id="average_load_hourly")
    # 00:10 daily — gives Kafka consumers a few minutes to flush last metrics
    scheduler.add_job(run_energy_balance, CronTrigger(hour=0, minute=10), id="energy_balance_daily")

    logger.info("Registered 2 scheduled jobs: average_load_hourly, energy_balance_daily")
