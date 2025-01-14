from fastapi import FastAPI, HTTPException
from storage.models import Task, CrawletUrl, Stats
from storage.repositories import TaskRepository, CrawledUrlRepository, get_engine

app = FastAPI()

task_repository = TaskRepository(get_engine())
crawled_url_repository = CrawledUrlRepository(get_engine())


@app.get("/tasks")
async def tasks(offset: int = 0, limit: int = 100) -> list[Task]:
    return await task_repository.get_list(offset, limit)


@app.post("/tasks")
async def create_task(task: Task) -> Task:
    return await task_repository.save(task)


@app.get("/tasks/{id}")
async def get_task(id: int) -> Task:
    task = await task_repository.get(id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/crawled-urls")
async def crawler_urls(offset: int = 0, limit: int = 100) -> list[CrawletUrl]:
    return await crawled_url_repository.get_list(offset, limit)


@app.get("/stats")
async def stats() -> Stats:
    return await crawled_url_repository.get_stats()
