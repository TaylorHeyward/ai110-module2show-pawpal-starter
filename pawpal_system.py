from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple


@dataclass
class Task:
    task_id: str
    title: str
    due_datetime: datetime
    priority: int = 3
    status: str = "pending"
    recurrence: Optional[str] = None

    def mark_done(self) -> None:
        """Mark the task as done (placeholder)."""
        pass

    def is_due_on(self, target_date: date) -> bool:
        """Return True if the task is due on target_date (placeholder)."""
        pass

    def next_occurrence(self) -> Optional[datetime]:
        """Compute the next occurrence for recurring tasks (placeholder)."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet (placeholder)."""
        pass

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by id; return True if removed (placeholder)."""
        pass

    def get_tasks_for_date(self, target_date: date) -> List[Task]:
        """Return tasks for the given date (placeholder)."""
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner (placeholder)."""
        pass

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name; return True if removed (placeholder)."""
        pass

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return a pet by name or None if not found (placeholder)."""
        pass


class PawPalSystem:
    def __init__(self, owners: Optional[Dict[str, Owner]] = None) -> None:
        self.owners: Dict[str, Owner] = owners if owners is not None else {}

    def add_owner(self, owner: Owner) -> None:
        """Add an owner to the system (placeholder)."""
        pass

    def schedule_task(self, owner_name: str, pet_name: str, task: Task) -> None:
        """Schedule a task for a pet of an owner (placeholder)."""
        pass

    def get_todays_tasks(self, target_date: date) -> List[Task]:
        """Return all tasks scheduled for target_date across owners/pets (placeholder)."""
        pass

    def detect_conflicts(self, target_date: date) -> List[Tuple[Task, Task]]:
        """Detect conflicting tasks on target_date (placeholder)."""
        pass

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by priority/due time (placeholder)."""
        pass