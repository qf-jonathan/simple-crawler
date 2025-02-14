import asyncio
import logging

from random import random
from crawler.crawler import crawl_url
from storage.repositories import TaskRepository, CrawledUrlRepository, get_engine
from storage.models import TaskState, Task

logger = logging.getLogger(__name__)

task_repository = TaskRepository(get_engine())
crawled_url_repository = CrawledUrlRepository(get_engine())


async def execute_task(task: Task):
    logger.info(f"Executing task {task.id} [{task.url}]")

    crawlet_urls = await crawl_url(
        task.url, task.max_depth, set(task.domains), set(task.blacklist)
    )

    for crawled_url in crawlet_urls:
        crawled_url.task_id = task.id

    await crawled_url_repository.save_many(crawlet_urls)
    task.state = TaskState.COMPLETED
    await task_repository.update(task)

    logger.info(f"Finished task {task.id} [{task.url}]")


async def worker():
    while True:
        # trick to minimize the posibility of race conditions
        await asyncio.sleep(random())

        task = await task_repository.get_to_run()
        if task is not None:
            await execute_task(task)

        await asyncio.sleep(1)
