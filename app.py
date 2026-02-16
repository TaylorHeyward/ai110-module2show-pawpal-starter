import streamlit as st
from datetime import datetime, date
from pawpal_system import Owner, Pet, Task, PawPalSystem

# Initialize persistent system in session_state
if "system" not in st.session_state:
    st.session_state.system = PawPalSystem()

# Ensure an owner object exists in session_state and is registered with the system
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Taylor")  # or "Default Owner"
    try:
        st.session_state.system.add_owner(st.session_state.owner)
    except ValueError:
        # owner already exists in system; ignore
        pass

# NOTE: This app requires Streamlit installed locally.
# Install with: pip install streamlit

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
st.header("Add a Pet")

with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name")
    species = st.text_input("Species")
    age = st.number_input("Age", min_value=0, step=1)
    notes = st.text_area("Notes (optional)")
    submitted = st.form_submit_button("Add Pet")

if submitted:
    try:
        new_pet = Pet(name=pet_name, species=species, age=int(age), notes=notes)
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added pet: {pet_name}")
    except Exception as e:
        st.error(str(e))
st.subheader("Your Pets")
if len(st.session_state.owner.pets) == 0:
    st.info("No pets added yet.")
else:
    for p in st.session_state.owner.pets:
        st.write(f"- {p.name} ({p.species}, age {p.age})")
pet_names = [p.name for p in st.session_state.owner.pets]
st.header("Schedule a Task")

if len(pet_names) == 0:
    st.warning("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form"):
        pet_name = st.selectbox("Choose a pet", pet_names)
        title = st.text_input("Task title (Walk, Feeding, Medication, Appointment)")
        due_date = st.date_input("Due date", value=date.today())
        due_time = st.time_input("Due time")
        priority = st.number_input("Priority (1 low, 5 high)", min_value=1, max_value=5, value=3, step=1)
        task_id = st.text_input("Task ID", value=f"task-{int(datetime.now().timestamp())}")
        submitted_task = st.form_submit_button("Add Task")

    if submitted_task:
        try:
            due_dt = datetime.combine(due_date, due_time)
            task = Task(
                task_id=task_id,
                title=title,
                due_datetime=due_dt,
                priority=int(priority),
            )
            st.session_state.system.schedule_task(st.session_state.owner.name, pet_name, task)
            st.success(f"Scheduled: {title} for {pet_name} at {due_dt.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            st.error(str(e))
st.header("Today's Schedule")

today = date.today()
tasks_today = st.session_state.system.get_todays_tasks(today)
# Sort tasks using backend sorter
if not tasks_today:
    st.info("No tasks scheduled for today.")
else:
    try:
        sorted_tasks = st.session_state.system.sort_tasks(tasks_today)
    except Exception:
        # fallback
        sorted_tasks = tasks_today

    # Build table rows
    rows = []
    for t in sorted_tasks:
        status_value = getattr(t.status, "value", str(t.status))
        time_str = t.due_datetime.strftime('%H:%M') if t.due_datetime is not None else "--:--"
        rows.append({"title": t.title, "time": time_str, "priority": t.priority, "status": status_value})

    st.table(rows)

    # Detect conflicts (interval overlaps) and show warnings
    try:
        conflicts = st.session_state.system.detect_conflicts(today)
    except Exception:
        conflicts = []

    if conflicts:
        msgs = []
        for a, b in conflicts:
            atime = a.due_datetime.strftime('%Y-%m-%d %H:%M') if a.due_datetime is not None else 'unknown'
            btime = b.due_datetime.strftime('%Y-%m-%d %H:%M') if b.due_datetime is not None else 'unknown'
            msgs.append(f"{a.title} ({atime}) conflicts with {b.title} ({btime})")
        st.warning("Conflicts detected:\n" + "\n".join(msgs))
