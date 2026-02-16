from datetime import datetime, date, timedelta

import pytest

from pawpal_system import PawPalSystem, Owner, Pet, Task, TaskStatus, Recurrence


def _make_system_with_owner_pet():
    system = PawPalSystem()
    owner = Owner(name="Taylor")
    pet = Pet(name="Fido", species="Dog", age=4)
    owner.add_pet(pet)
    system.add_owner(owner)
    return system, owner, pet


def test_sorting_correctness_chronological_order():
    system, owner, pet = _make_system_with_owner_pet()

    # Add tasks out of order
    t1 = Task(task_id="t1", title="Afternoon", due_datetime=datetime(2026, 2, 15, 15, 0), priority=1)
    t2 = Task(task_id="t2", title="Morning", due_datetime=datetime(2026, 2, 15, 9, 0), priority=1)
    t3 = Task(task_id="t3", title="Noon", due_datetime=datetime(2026, 2, 15, 12, 0), priority=1)

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    tasks_today = system.get_todays_tasks(date(2026, 2, 15))
    sorted_tasks = system.sort_by_time(tasks_today)

    times = [t.due_datetime for t in sorted_tasks]
    assert times == sorted(times)


def test_recurrence_daily_creates_next_task_on_complete():
    system, owner, pet = _make_system_with_owner_pet()

    base_dt = datetime(2026, 2, 15, 9, 0)
    daily = Task(
        task_id="daily1",
        title="Daily walk",
        due_datetime=base_dt,
        priority=2,
        recurrence=Recurrence(freq="daily", interval=1),
    )
    pet.add_task(daily)

    # Mark complete using your system flow
    # If you implemented a system-level completion method, use it.
    # Otherwise, call mark_done and verify your automation.
    if hasattr(system, "mark_task_complete"):
        system.mark_task_complete(owner.name, pet.name, "daily1")
    else:
        daily.mark_done()

    # There should now be a new task due the next day
    next_day = base_dt + timedelta(days=1)
    matching = [t for t in pet.tasks if t.title == "Daily walk" and t.due_datetime == next_day]
    assert len(matching) == 1, "Expected a new daily occurrence for the next day"
    assert matching[0].status == TaskStatus.PENDING


def test_conflict_detection_flags_duplicate_times():
    system, owner, pet = _make_system_with_owner_pet()

    dt = datetime(2026, 2, 15, 9, 0)
    a = Task(task_id="a", title="Walk", due_datetime=dt, priority=2)
    b = Task(task_id="b", title="Medication", due_datetime=dt, priority=5)

    pet.add_task(a)
    pet.add_task(b)

    conflicts = system.detect_conflicts(date(2026, 2, 15))
    assert len(conflicts) >= 1
    # conflict should contain the two tasks in some order
    flat = [(x.task_id, y.task_id) for x, y in conflicts]
    assert ("a", "b") in flat or ("b", "a") in flat


def test_pet_with_no_tasks_returns_empty_list():
    system, owner, pet = _make_system_with_owner_pet()
    # Remove any tasks if present
    pet.tasks.clear()

    tasks_today = system.get_todays_tasks(date(2026, 2, 15))
    assert tasks_today == []

