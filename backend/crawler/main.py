import asyncio
import logging

from crawler.worker import worker
from storage.repositories import init_db, get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)

WORKER_COUNT = 3


async def main():
    await init_db(get_engine())
    semaphore = asyncio.Semaphore(WORKER_COUNT)
    workers = [worker(semaphore) for _ in range(WORKER_COUNT)]
    logger.info("Service workers started")
    await asyncio.gather(*workers)


asyncio.run(main())
