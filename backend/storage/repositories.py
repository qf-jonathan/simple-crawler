import asyncio
from random import random
from functools import lru_cache
from storage.models import SQLModel, Task, CrawletUrl, TaskState, Stats, DomainStats
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from typing import TypeVar, Generic
from collections import Counter
from urllib.parse import urlparse
from settings import SQLALCHEMY_DATABASE_URL

T = TypeVar("T", bound=SQLModel)


@lru_cache(maxsize=1)
def get_engine():
    return create_async_engine(SQLALCHEMY_DATABASE_URL)


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


class BaseRepository(Generic[T]):
    def __init__(self, model: T, engine: AsyncEngine):
        self.model = model
        self.engine = engine

    async def save(self, instance: T) -> T:
        async with AsyncSession(self.engine) as session:
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def save_many(self, instance_list: list[T]):
        async with AsyncSession(self.engine) as session:
            session.add_all(instance_list)
            await session.commit()

    async def update(self, instance: T) -> T:
        async with AsyncSession(self.engine) as session:
            existing_instance = await session.get(self.model, instance.id)
            if not existing_instance:
                raise ValueError("Instance not found")

            for key, value in instance.model_dump(exclude_unset=True).items():
                setattr(existing_instance, key, value)
            session.add(existing_instance)
            await session.commit()
            await session.refresh(existing_instance)
            return instance

    async def get(self, id: int) -> T | None:
        async with AsyncSession(self.engine) as session:
            return await session.get(self.model, id)

    async def get_list(self, offset: int = 0, limit: int = 100) -> list[T]:
        async with AsyncSession(self.engine) as session:
            result = await session.exec(select(self.model).offset(offset).limit(limit))
            return result.all()


class TaskRepository(BaseRepository[Task]):
    def __init__(self, engine: AsyncEngine):
        super().__init__(Task, engine)

    async def get_list_by_state(
        self, state: TaskState, offset: int = 0, limit: int = 100
    ) -> list[Task]:
        async with AsyncSession(self.engine) as session:
            result = await session.exec(
                select(Task).where(Task.state == state).offset(offset).limit(limit)
            )
            return result.all()

    async def get_to_run(self) -> int | None:
        await asyncio.sleep(random())
        async with AsyncSession(self.engine) as session:
            result = await session.exec(
                select(Task).where(Task.state == TaskState.PENDING).limit(1)
            )
            task = result.one_or_none()
            if task is None:
                return None
            task.state = TaskState.RUNNING
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task


class CrawledUrlRepository(BaseRepository[CrawletUrl]):
    def __init__(self, engine: AsyncEngine):
        super().__init__(CrawletUrl, engine)

    async def get_stats(self) -> Stats:
        async with AsyncSession(self.engine) as session:
            result = await session.exec(select(CrawletUrl))
            crawled_urls = result.all()

        total_crawled_urls = len(crawled_urls)
        total_errors_during_crawling = sum(
            1 for url in crawled_urls if url.status_code >= 400
        )
        status_code_stats = Counter([url.status_code for url in crawled_urls])
        domain_stats = Counter([urlparse(url.url).netloc for url in crawled_urls])

        return Stats(
            total_crawled_urls=total_crawled_urls,
            total_errors_during_crawling=total_errors_during_crawling,
            status_code_stats=status_code_stats,
            domain_stats=[
                DomainStats(domain=domain, total_crawled_urls=count)
                for domain, count in domain_stats.items()
            ],
        )
