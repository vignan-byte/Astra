from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    queued = "queued"
    planning = "planning"
    awaiting_confirmation = "awaiting_confirmation"
    running = "running"
    complete = "complete"
    failed = "failed"


class Permission(str, Enum):
    read = "read"
    confirm = "confirm"
    blocked = "blocked"


class TaskCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    prompt: str
    status: TaskStatus = TaskStatus.queued
    plan: list[str] = Field(default_factory=list)
    result: str | None = None
    confirmation_token: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Confirmation(BaseModel):
    token: str


class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    kind: str = "note"


class Memory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    content: str
    kind: str
    created_at: datetime = Field(default_factory=utcnow)


class AuditEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=utcnow)
    task_id: UUID | None = None
    category: str
    action: str
    permission: Permission
    details: dict[str, Any] = Field(default_factory=dict)
