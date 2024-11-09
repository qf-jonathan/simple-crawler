from sqlmodel import SQLModel, Field, Column, JSON
from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    url: str
    max_depth: int = Field(default=1, ge=1)
    domains: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    blacklist: list[str] = Field(sa_column=Column(JSON), default_factory=list)
    state: TaskState = Field(default=TaskState.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)


class CrawletUrl(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    url: str
    status_code: int | None
    content_size: int | None
    content_title: str | None
    created_at: datetime = Field(default_factory=datetime.now)
    task_id: int | None = Field(default=None, foreign_key="task.id")
    links: list[str] = Field(sa_column=Column(JSON), default_factory=list)


class DomainStats(BaseModel):
    domain: str
    total_crawled_urls: int


class Stats(BaseModel):
    total_crawled_urls: int
    total_errors_during_crawling: int
    status_code_stats: dict[int, int]
    domain_stats: list[DomainStats]
