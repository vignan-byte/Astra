from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import UUID

from .models import AuditEvent, Memory, Task, TaskStatus


class Store:
    def __init__(self, db_path: Path) -> None:
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY, prompt TEXT NOT NULL, status TEXT NOT NULL,
                plan TEXT NOT NULL, result TEXT, confirmation_token TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY, content TEXT NOT NULL, kind TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, task_id TEXT, category TEXT NOT NULL,
                action TEXT NOT NULL, permission TEXT NOT NULL, details TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def save_task(self, task: Task) -> Task:
        self.connection.execute(
            "INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (str(task.id), task.prompt, task.status.value, json.dumps(task.plan), task.result,
             task.confirmation_token, task.created_at.isoformat(), task.updated_at.isoformat()),
        )
        self.connection.commit()
        return task

    def get_task(self, task_id: UUID) -> Task | None:
        row = self.connection.execute("SELECT * FROM tasks WHERE id = ?", (str(task_id),)).fetchone()
        return self._task(row) if row else None

    def list_tasks(self, limit: int = 30) -> list[Task]:
        rows = self.connection.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._task(row) for row in rows]

    def _task(self, row: sqlite3.Row) -> Task:
        return Task(id=row["id"], prompt=row["prompt"], status=TaskStatus(row["status"]),
                    plan=json.loads(row["plan"]), result=row["result"], confirmation_token=row["confirmation_token"],
                    created_at=row["created_at"], updated_at=row["updated_at"])

    def save_memory(self, memory: Memory) -> Memory:
        self.connection.execute("INSERT INTO memories VALUES (?, ?, ?, ?)",
            (str(memory.id), memory.content, memory.kind, memory.created_at.isoformat()))
        self.connection.commit()
        return memory

    def list_memories(self, query: str = "", limit: int = 30) -> list[Memory]:
        rows = self.connection.execute(
            "SELECT * FROM memories WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?", (f"%{query}%", limit)
        ).fetchall()
        return [Memory(id=row["id"], content=row["content"], kind=row["kind"], created_at=row["created_at"]) for row in rows]

    def audit(self, event: AuditEvent) -> None:
        self.connection.execute("INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(event.id), event.timestamp.isoformat(), str(event.task_id) if event.task_id else None,
             event.category, event.action, event.permission.value, json.dumps(event.details)))
        self.connection.commit()

    def list_audit(self, limit: int = 50) -> list[AuditEvent]:
        rows = self.connection.execute("SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        return [AuditEvent(id=r["id"], timestamp=r["timestamp"], task_id=r["task_id"], category=r["category"],
            action=r["action"], permission=r["permission"], details=json.loads(r["details"])) for r in rows]
