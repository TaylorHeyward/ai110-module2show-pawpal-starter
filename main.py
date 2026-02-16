from datetime import datetime, date
from pawpal_system import Owner, Pet, Task, PawPalSystem

def main():
    system = PawPalSystem()

    owner = Owner(name="Taylor")
    system.add_owner(owner)

    dog = Pet(name="Fido", species="Dog", age=4)
    cat = Pet(name="Whiskers", species="Cat", age=2)

    owner.add_pet(dog)
    owner.add_pet(cat)

    task1 = Task(
        task_id="t1",
        title="Morning walk",
        due_datetime=datetime(2026, 2, 15, 9, 0),
        priority=2
    )

    task2 = Task(
        task_id="t2",
        title="Medication",
        due_datetime=datetime(2026, 2, 15, 9, 0),
        priority=5
    )

    task3 = Task(
        task_id="t3",
        title="Grooming",
        due_datetime=datetime(2026, 2, 15, 15, 0),
        priority=1
    )

    system.schedule_task("Taylor", "Fido", task1)
    system.schedule_task("Taylor", "Fido", task2)
    system.schedule_task("Taylor", "Whiskers", task3)

    today = date(2026, 2, 15)
    tasks_today = system.get_todays_tasks(today)

    print(f"\nToday's Schedule ({today}):")
    for task in tasks_today:
        print(f"- [{task.status}] {task.title} "
              f"at {task.due_datetime.strftime('%H:%M')} "
              f"priority={task.priority}"
              )

    # Detect exact-time conflicts and print warnings
    warnings = system.detect_exact_time_conflicts(today)
    if warnings:
        print("\nConflicts detected:")
        for w in warnings:
            print("- "+w)

if __name__ == "__main__":
    main()

