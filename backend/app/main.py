from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import AgentEngine
from .models import Confirmation, Memory, MemoryCreate, Task, TaskCreate
from .policy import PolicyEngine
from .store import Store

store = Store(Path(__file__).parent.parent / "astra.db")
engine = AgentEngine(store, PolicyEngine())
app = FastAPI(title="ASTRA Agent OS", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
    ],
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health(): return {"status": "online", "services": {"brain": "ready", "memory": "ready", "policy": "ready"}}

@app.post("/tasks", response_model=Task)
def create_task(payload: TaskCreate): return engine.submit(Task(prompt=payload.prompt))

@app.get("/tasks", response_model=list[Task])
def tasks(): return store.list_tasks()

@app.post("/tasks/{task_id}/confirm", response_model=Task)
def confirm_task(task_id: UUID, payload: Confirmation):
    task = store.get_task(task_id)
    if not task: raise HTTPException(404, "Task not found")
    try: return engine.confirm(task, payload.token)
    except ValueError as error: raise HTTPException(400, str(error))

@app.get("/memory", response_model=list[Memory])
def memories(q: str = ""): return store.list_memories(q)

@app.post("/memory", response_model=Memory)
def create_memory(payload: MemoryCreate): return store.save_memory(Memory(content=payload.content, kind=payload.kind))

@app.get("/audit")
def audit(): return store.list_audit()
