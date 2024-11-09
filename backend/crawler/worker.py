import asyncio

from crawler.crawler import crawl_url
from storage.repositories import (
    TaskRepository,
    init_db,
    CrawledUrlRepository,
    get_engine,
)
from storage.models import TaskState, Task

task_repository = TaskRepository(get_engine())
crawled_url_repository = CrawledUrlRepository(get_engine())


async def execute_task(task: Task):
    crawlet_urls = await crawl_url(task.url, task.max_depth)

    for crawled_url in crawlet_urls:
        crawled_url.task_id = task.id

    await crawled_url_repository.save_many(crawlet_urls)
    task.state = TaskState.COMPLETED
    await task_repository.update(task)


async def worker(semaphore: asyncio.Semaphore):
    while True:
        async with semaphore:
            task = await task_repository.get_to_run()
            if task is not None:
                await execute_task(task)
        await asyncio.sleep(1)


async def main():
    await init_db(get_engine())

    workers_count = 3
    semaphore = asyncio.Semaphore(workers_count)
    workers = [worker(semaphore) for _ in range(workers_count)]
    await asyncio.gather(*workers)


asyncio.run(main())
