import asyncio
import logging

from crawler.worker import worker
from storage.repositories import init_db, get_engine
from settings import CRAWLER_WORKERS_COUNT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


async def main():
    await init_db(get_engine())
    workers = [worker() for _ in range(CRAWLER_WORKERS_COUNT)]
    logger.info("Service workers started")
    await asyncio.gather(*workers)


asyncio.run(main())
