# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Before designing the system, I identified three core actions the user should be able to perform. 
First, a user should be able to add and manage pets, since all care tasks are tied to a specific animal. 
Second, the user should be able to schedule care tasks such as feedings, walks, medications, or appointments, including recurring tasks for daily routines. 
Third, the user should be able to view all tasks for the current day across pets, prioritized by time and urgency, so they can clearly see what needs attention.

For the initial design, I identified four main objects: Owner, Pet, Task, and PawPalSystem. 
The Owner class stores basic user information and manages a collection of pets. 
Each Pet holds identifying details and a list of care tasks associated with that animal. 
Tasks represent individual responsibilities such as feedings, walks, or appointments and store information like due time, priority, and recurrence. 
The PawPalSystem class acts as the coordinator, handling task scheduling, sorting, and conflict detection across pets and owners.

**b. Design changes**

classDiagram
class Owner {
  +str name
  +list pets
  +add_pet(pet: Pet) void
  +remove_pet(pet_name: str) bool
  +get_pet(pet_name: str) Pet
}

class Pet {
  +str name
  +str species
  +int age
  +str notes
  +list tasks
  +add_task(task: Task) void
  +remove_task(task_id: str) bool
  +get_tasks_for_date(date) list
}

class Task {
  +str task_id
  +str title
  +datetime due_datetime
  +int priority
  +str status
  +str recurrence
  +mark_done() void
  +is_due_on(date) bool
  +next_occurrence() datetime
}

class PawPalSystem {
  +dict owners
  +add_owner(owner: Owner) void
  +schedule_task(owner_name: str, pet_name: str, task: Task) void
  +get_todays_tasks(date) list
  +detect_conflicts(date) list
  +sort_tasks(tasks: list) list
}

Owner "1" o-- "*" Pet : owns
Pet "1" o-- "*" Task : has
PawPalSystem "1" o-- "*" Owner : manages

After reviewing the class skeleton with AI feedback, no major structural changes were needed. 
The existing relationships between Owner, Pet, Task, and PawPalSystem were sufficient to support scheduling, prioritization, and conflict detection. 
Any suggested improvements were implementation-level details that did not require changes to the overall design.

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

I chose a lightweight conflict rule that only flags tasks scheduled at the exact same due_datetime, instead of checking whether task intervals overlap. This keeps the scheduler simple and fast for a CLI-focused MVP, but it means longer tasks that overlap in time won't be reported as conflicts. For my use-case—mostly short, point-in-time care actions like feedings and meds—this tradeoff is acceptable and avoids adding interval math and timezone complexity. If users later need richer detection, it can be extended to compare start/end intervals.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

- I tested core flows: scheduling a task, retrieving today's tasks, sorting by due time and priority, detecting exact-time conflicts, and the recurring-task completion that creates the next occurrence.
- These tests cover the user-facing behaviors the CLI and Streamlit UI depend on, so they catch regressions in the scheduler's core responsibilities.

**b. Confidence**

- I'm moderately confident: unit tests cover the main happy paths and the lightweight conflict/recurrence rules, and they all pass in the current suite.
- Next edge cases I'd add: timezone/DST handling, tasks with durations that span days (interval overlaps), recurrence limits (until/count), and ambiguous owner/pet name collisions.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

- I’m most satisfied with getting a working end-to-end scheduler: the dataclass models, recurring-task flow, basic conflict detection, and a small Streamlit demo all tie together.

**b. What I would improve**

- In a future iteration I'd formalize recurrence using a library (rrule), make all datetimes timezone-aware, and add persistent storage so the system scales beyond a single-session CLI/demo.

**c. Key takeaway**

- Working with AI accelerated design and iteration, but it amplified the need for clear contracts: I had to decide where responsibilities live (Task vs PawPalSystem), validate suggestions with tests, and be the final architect making trade-offs.

---

### AI collaboration notes

- How Copilot helped: It assisted across phases — sketching UML, generating class skeletons, proposing recurrence/conflict approaches, and producing small, testable implementations and examples.
- One AI suggestion I modified: I rejected a free-form recurrence string in favor of a structured Recurrence dataclass (or rrule later) because free strings are brittle for computing next occurrences.
- Separating chat sessions improved organization: each session focused on a single feature (scheduling, recurrence, conflicts, UI), which made iterations and rollbacks easier.
- As lead architect I learned to treat AI output as a draft: I evaluated suggestions against system contracts, added tests, and kept final control over design choices and trade-offs.
