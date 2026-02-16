from __future__ import annotations

from asyncio import tasks
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
import uuid
from typing import List, Dict, Optional, Tuple


class TaskStatus(Enum):
    PENDING = "pending"
    DONE = "done"
    SKIPPED = "skipped"


@dataclass
class Recurrence:
    """A minimal, structured recurrence placeholder.

    For a production system prefer using dateutil.rrule or a richer model.
    """
    freq: str  # e.g. 'daily', 'weekly', 'monthly'
    interval: int = 1
    count: Optional[int] = None
    until: Optional[date] = None


@dataclass
class Task:
    """Task represents a schedulable item.

    Notes:
    - Prefer timezone-aware datetimes. This skeleton accepts datetimes and
      callers should normalize to UTC before storing.
    - Both a start time and/or a due time are supported. Duration is optional.
    - task_id defaults to a UUID string to avoid collisions on human names.
    """

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    # Prefer start_datetime for interval tasks. due_datetime can be used for
    # deadline-style tasks.
    start_datetime: Optional[datetime] = None
    due_datetime: Optional[datetime] = None
    duration: Optional[timedelta] = None
    priority: int = 3
    status: TaskStatus = TaskStatus.PENDING
    recurrence: Optional[Recurrence] = None
    # optional link to parent pet id (system may populate this)
    pet_id: Optional[str] = None

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.status = TaskStatus.DONE

    def is_due_on(self, target_date: date) -> bool:
        """Return True if this task (or an occurrence) falls on target_date."""
        if self.due_datetime is None:
            return False

        base_date = self.due_datetime.date()
        # No recurrence: due date must match exactly
        if not self.recurrence:
            return base_date == target_date

        # Simple recurrence: support 'daily' and 'weekly' with interval in Recurrence
        delta_days = (target_date - base_date).days
        if delta_days < 0:
            return False

        freq = self.recurrence.freq if isinstance(self.recurrence, Recurrence) else None
        interval = self.recurrence.interval if isinstance(self.recurrence, Recurrence) else 1

        if freq == "daily":
            return (delta_days % interval) == 0
        if freq == "weekly":
            return ((delta_days // 7) % interval) == 0

        # Unknown recurrence type; be conservative
        return False

    def next_occurrence(self) -> Optional[datetime]:
        """Return the next occurrence datetime for recurring tasks, if any."""
        if self.due_datetime is None or not self.recurrence:
            return None

        now = datetime.now(self.due_datetime.tzinfo)
        base = self.due_datetime

        freq = self.recurrence.freq
        interval = self.recurrence.interval

        if freq == "daily":
            days = (now.date() - base.date()).days
            if days < 0:
                return base
            # how many intervals have passed
            steps = (days // interval) + 1
            return datetime.combine(base.date() + timedelta(days=steps * interval), base.time())

        if freq == "weekly":
            days = (now.date() - base.date()).days
            if days < 0:
                return base
            weeks = (days // 7)
            steps = (weeks // interval) + 1
            return datetime.combine(base.date() + timedelta(weeks=steps * interval), base.time())

        return None


@dataclass
class Pet:
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)
    pet_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet (in-memory only)."""
        # attach lightweight back-reference and store
        task.pet_id = getattr(self, "pet_id", None)
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by its id; return True if removed."""
        for i, t in enumerate(self.tasks):
            if t.task_id == task_id:
                del self.tasks[i]
                return True
        return False

    def get_tasks_for_date(self, target_date: date) -> List[Task]:
        """Return tasks (including recurring occurrences) that fall on target_date."""
        results: List[Task] = []
        for t in self.tasks:
            try:
                if t.is_due_on(target_date):
                    results.append(t)
            except Exception:
                # be forgiving for placeholder implementations
                continue
        return results


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    owner_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, rejecting duplicate names."""
        # disallow duplicate pet names for simplicity
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"Pet with name '{pet.name}' already exists for owner '{self.name}'")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name; return True if removed."""
        for i, p in enumerate(self.pets):
            if p.name == pet_name:
                del self.pets[i]
                return True
        return False

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return a pet by name, or None if not found."""
        for p in self.pets:
            if p.name == pet_name:
                return p
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks belonging to this owner's pets."""
        results: List[Task] = []
        for p in self.pets:
            results.extend(p.tasks)
        return results


class PawPalSystem:
    """Top-level system managing owners, pets and tasks.

    Responsibilities to keep here:
    - global owner/pet lookup and uniqueness (IDs)
    - normalization of datetimes (tz)
    - recurrence expansion for cross-owner queries
    - conflict detection and global sorting
    """

    def sort_by_time(self, tasks):
        """Return tasks sorted by due time."""
        return sorted(tasks, key=lambda t: t.due_datetime)

    def filter_by_status(self, tasks, status):
        """Return tasks filtered by completion status."""
        return [t for t in tasks if t.status == status]

    def __init__(self, owners: Optional[Dict[str, Owner]] = None) -> None:
        """Create a new PawPalSystem with an optional initial owners mapping."""
        # owners keyed by owner_id (not owner.name) to avoid collisions
        self.owners: Dict[str, Owner] = owners if owners is not None else {}

    def add_owner(self, owner: Owner) -> None:
        """Register a new owner in the system, rejecting duplicate names."""
        if owner.name in self.owners:
            raise ValueError(f"Owner with name '{owner.name}' already exists")
        self.owners[owner.name] = owner

    def schedule_task(self, owner_id: str, pet_id: str, task: Task) -> None:
        """Schedule a task for the named owner and pet, validating existence."""
        # This method signature is kept backward-compatible with owner_id/pet_id
        # but we also support name-based scheduling via owner name and pet name.
        # Attempt to resolve owner by name first (common CLI case).
        owner = self.owners.get(owner_id)
        if owner is None:
            raise ValueError(f"Owner '{owner_id}' not found")

        # find pet by id or name
        pet = None
        for p in owner.pets:
            if getattr(p, "pet_id", None) == pet_id or p.name == pet_id:
                pet = p
                break

        if pet is None:
            raise ValueError(f"Pet '{pet_id}' not found for owner '{owner.name}'")

        # attach pet reference and add
        task.pet_id = getattr(pet, "pet_id", None)
        pet.add_task(task)

    def mark_task_complete(self, owner_name: str, pet_name: str, task_id: str) -> None:
        """Mark a task done and, if recurring daily/weekly, schedule the next occurrence."""
        owner = self.owners.get(owner_name)
        if owner is None:
            raise ValueError(f"Owner '{owner_name}' not found")

        pet = owner.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"Pet '{pet_name}' not found for owner '{owner_name}'")

        # find the task
        task = None
        for t in pet.tasks:
            if t.task_id == task_id:
                task = t
                break

        if task is None:
            raise ValueError(f"Task '{task_id}' not found for pet '{pet_name}'")

        # mark original done
        task.mark_done()

        # if recurring daily or weekly, create next occurrence
        if isinstance(task.recurrence, Recurrence) and task.due_datetime is not None:
            freq = task.recurrence.freq
            if freq == "daily":
                delta = timedelta(days=1)
            elif freq == "weekly":
                delta = timedelta(weeks=1)
            else:
                return

            new_due = task.due_datetime + delta
            new_task = Task(
                title=task.title,
                due_datetime=new_due,
                priority=task.priority,
                duration=task.duration,
                recurrence=task.recurrence,
            )
            new_task.pet_id = task.pet_id
            pet.add_task(new_task)

    def get_todays_tasks(self, target_date: date) -> List[Task]:
        """Return all tasks due on target_date across all owners and pets."""
        # Return tasks due on target_date across all owners and pets
        results: List[Task] = []
        for owner in self.owners.values():
            for pet in owner.pets:
                results.extend(pet.get_tasks_for_date(target_date))
        return results

    def detect_conflicts(self, target_date: date) -> List[Tuple[Task, Task]]:
        """Detect pairs of tasks that overlap on target_date."""
        # Build occurrences list with start/end
        occs: List[Tuple[Task, datetime, datetime]] = []
        for owner in self.owners.values():
            for pet in owner.pets:
                for t in pet.get_tasks_for_date(target_date):
                    start = t.due_datetime
                    end = start + t.duration if (t.duration is not None) else start
                    occs.append((t, start, end))

        # sort by start
        occs.sort(key=lambda x: x[1])

        conflicts: List[Tuple[Task, Task]] = []
        # naive O(n^2) for small lists: compare each pair where starts overlap
        for i in range(len(occs)):
            ti, si, ei = occs[i]
            for j in range(i + 1, len(occs)):
                tj, sj, ej = occs[j]
                # overlap if the later start is strictly before the earlier end.
                # Use strict < so that two instantaneous tasks at the same
                # timestamp (start == end) are not considered a conflict.
                if sj < ei:
                    conflicts.append((ti, tj))
                else:
                    # since sorted by start, no further overlaps for i
                    break

        return conflicts

    def detect_exact_time_conflicts(self, target_date: date) -> List[str]:
        """Return warning strings for tasks that share the exact same due_datetime on target_date."""
        # Map datetime -> list of (owner, pet, task)
        groups: Dict[datetime, List[Tuple[Owner, Pet, Task]]] = {}
        for owner in self.owners.values():
            for pet in owner.pets:
                for t in pet.get_tasks_for_date(target_date):
                    if t.due_datetime is None:
                        continue
                    dt = t.due_datetime
                    groups.setdefault(dt, []).append((owner, pet, t))

        warnings: List[str] = []
        for dt, entries in groups.items():
            if len(entries) > 1:
                # create a single warning summarizing all tasks at this datetime
                parts = []
                for owner, pet, t in entries:
                    parts.append(f"{owner.name}/{pet.name}:{t.title} (id={t.task_id})")
                warnings.append(f"Conflict at {dt}: " + ", ".join(parts))

        return warnings

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by due datetime (earlier first), then priority (higher first)."""
        # Sort by due_datetime (earlier first) then by priority (higher first)
        def key_fn(t: Task):
            dd = t.due_datetime if t.due_datetime is not None else datetime.max
            return (dd, -t.priority)

        return sorted(tasks, key=key_fn)


if __name__ == "__main__":
    # Small demo: create system, owner, pet, and a few tasks; print today's tasks
    system = PawPalSystem()
    owner = Owner(name="Alice")
    system.add_owner(owner)

    pet = Pet(name="Fido", species="dog", age=4)
    owner.add_pet(pet)

    now = datetime.now()
    t1 = Task(title="Morning walk", due_datetime=now.replace(hour=9, minute=0, second=0, microsecond=0), priority=2)
    t2 = Task(title="Medication", due_datetime=now.replace(hour=9, minute=0, second=0, microsecond=0), priority=5)
    t3 = Task(title="Grooming", due_datetime=now.replace(hour=15, minute=0, second=0, microsecond=0), priority=1,
              recurrence=Recurrence(freq="weekly", interval=1))

    system.schedule_task(owner.name, pet.name, t1)
    system.schedule_task(owner.name, pet.name, t2)
    system.schedule_task(owner.name, pet.name, t3)

    today = date.today()
    todays = system.get_todays_tasks(today)
    print(f"Tasks for {today}:")
    for t in system.sort_tasks(todays):
        pet_info = next((p for o in system.owners.values() for p in o.pets if getattr(p, 'pet_id', None) == t.pet_id), None)
        pet_name = pet_info.name if pet_info is not None else "<unknown>"
        print(f"- [{t.status.value}] {t.title} (pet: {pet_name}) at {t.due_datetime} priority={t.priority}")

    conflicts = system.detect_conflicts(today)
    if conflicts:
        print("Conflicts detected:")
        for a, b in conflicts:
            print(f"- {a.title} conflicts with {b.title} at {a.due_datetime}")

    # Demonstrate marking a recurring task done and auto-creating the next occurrence
    print("\nMarking recurring task 'Grooming' done and creating next occurrence...")
    system.mark_task_complete(owner.name, pet.name, t3.task_id)

    print(f"Tasks for pet {pet.name} after completion:")
    for t in pet.tasks:
        print(f"- [{t.status.value}] {t.title} at {t.due_datetime} (id={t.task_id})")
