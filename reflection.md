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

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
