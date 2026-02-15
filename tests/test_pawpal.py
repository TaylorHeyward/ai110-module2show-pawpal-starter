from datetime import datetime
from pawpal_system import Task, Pet


def test_task_completion_changes_status():
    task = Task(
        task_id="t1",
        title="Medication",
        due_datetime=datetime(2026, 2, 15, 9, 0),
        priority=3,
    )

    # Adjust this line if your method is named mark_done() instead of mark_complete()
    if hasattr(task, "mark_complete"):
        task.mark_complete()
    else:
        task.mark_done()

    status_value = getattr(task.status, "value", task.status)
    assert status_value in ("done", "completed"), f"Unexpected status: {task.status}"


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Fido", species="Dog", age=4)

    initial_count = len(pet.tasks)

    task = Task(
        task_id="t2",
        title="Morning walk",
        due_datetime=datetime(2026, 2, 15, 9, 0),
        priority=2,
    )

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
