from __future__ import annotations

import secrets
from datetime import datetime, timezone

from .models import AuditEvent, Permission, Task, TaskStatus
from .policy import PolicyEngine
from .store import Store
from .tools.computer import open_application


class AgentEngine:
    def __init__(self, store: Store, policy: PolicyEngine) -> None:
        self.store = store
        self.policy = policy

    def submit(self, task: Task) -> Task:
        task.status = TaskStatus.planning
        task.plan = self._plan(task.prompt)

        permission = self.policy.classify(task.prompt)

        self.store.audit(
            AuditEvent(
                task_id=task.id,
                category="agent",
                action="plan",
                permission=permission,
                details={"steps": len(task.plan)},
            )
        )

        if permission is Permission.blocked:
            task.status = TaskStatus.failed
            task.result = "Blocked by ASTRA security policy."

        elif permission is Permission.confirm:
            task.status = TaskStatus.awaiting_confirmation
            task.confirmation_token = secrets.token_urlsafe(16)
            task.result = (
                "This action could affect external systems. "
                "Confirm it in ASTRA to continue."
            )

        else:
            task.status = TaskStatus.running

            try:
                task.result = self._execute(task)
                task.status = TaskStatus.complete
            except Exception as exc:
                task.status = TaskStatus.failed
                task.result = f"Execution failed: {exc}"

        task.updated_at = datetime.now(timezone.utc)
        return self.store.save_task(task)

    def confirm(self, task: Task, token: str) -> Task:
        if (
            task.status is not TaskStatus.awaiting_confirmation
            or token != task.confirmation_token
        ):
            raise ValueError("Invalid or expired confirmation token")

        task.status = TaskStatus.running
        task.result = self._execute(task)
        task.confirmation_token = None
        task.status = TaskStatus.complete
        task.updated_at = datetime.now(timezone.utc)

        return self.store.save_task(task)

    def _plan(self, prompt: str) -> list[str]:
        return [
            "Interpret the user's request",
            "Select the appropriate ASTRA tool",
            "Execute the action",
            "Verify the result",
        ]

    def _execute(self, task: Task) -> str:
        prompt = task.prompt.lower().strip()

        if "open chrome" in prompt or "open google chrome" in prompt:
            result = open_application("chrome")

        elif "open notepad" in prompt:
            result = open_application("notepad")

        elif "open calculator" in prompt or "open calc" in prompt:
            result = open_application("calculator")

        elif "open paint" in prompt:
            result = open_application("paint")

        elif "open file explorer" in prompt or "open explorer" in prompt:
            result = open_application("explorer")

        else:
            result = {
                "success": False,
                "message": "ASTRA does not yet have a tool for this command.",
            }

        self.store.audit(
            AuditEvent(
                task_id=task.id,
                category="execution",
                action="tool_execution",
                permission=Permission.read,
                details={
                    "result": result,
                    "prompt": task.prompt,
                },
            )
        )

        if result.get("success") and result.get("verified"):
            return result["message"]

        if result.get("success"):
            return result["message"]

        return result.get("message", "ASTRA could not complete the action.")
