# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**Core User Actions**

1. **Add a pet care task** – Create a care task (walk, feeding, medication, grooming) with duration and priority.
2. **Generate a daily care plan** – Produce an optimized schedule based on available time windows, task priority, and preferences, with reasoning for why tasks were ordered that way.
3. **Enter pet and owner information** – Input owner details (name, availability) and pet details (name, category, special needs) so the planner can personalize recommendations.
4. **Authenticate / manage account** – Register and log in so pet profiles, task history, and schedules persist across sessions.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

My design evolved during implementation. Here are the key changes:

- **Added task completion tracking to "Task"**: Initially, "Task" only represented care activities to schedule, so I added "completed: bool" and "completed_at: datetime" fields, plus a "mark_complete()" method to support task history and persistence across sessions. Pet owners need to track which tasks were actually completed, not just scheduled. This enables future features like habit tracking and performance analytics.

- **Added "care_plans" to "User"**: Originally, "DailyCarePlan" existed independently without a direct link to users, so I added a "care_plans: List[DailyCarePlan]" collection and "add_care_plan()" method to "User" to make sure that users can access their historical schedules and generate plans.

- **Added "pets" to "DailyCarePlan"**: "DailyCarePlan" originally only contained "scheduled_tasks", so I added "pets: List[Pet]" to explicitly track which pets are included in each plan

- **Introduced "CarePlanScheduler" class**: Originally, scheduling logic was missing and only data structures existed, so I created a new class responsible for generating plans and detecting conflicts.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers these constraints in order of importance:

- **Owner availability (TimeWindow)**: tasks must fit within available windows.
- **Task duration**: a task must fit the remaining time in a window.
- **Task priority**: higher priority tasks are placed before lower priority ones.
- **Scheduled_time (if set)**: tasks with explicit scheduled times are respected when possible.
- **Recurrence and completion state**: recurring tasks are rescheduled only if due and uncompleted.

Decision rationale: availability and duration are hard constraints (a task cannot occur outside available time), so they are enforced first. Priority and scheduled_time guide ordering within feasible slots to produce useful, explainable plans for typical daily workloads.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Key Tradeoff (Greedy vs. Optimal):
This scheduler uses a greedy left-to-right bin-packing approach: it processes
tasks in priority order and places each into the first available time slot.
This is O(n \* w) where n = tasks and w = availability windows, making it fast
for typical daily schedules (5–20 tasks, 2–3 windows).

Trade-off: Greedy placement may not find the globally optimal arrangement.
For example, if a high-priority 30-min task arrives after two low-priority
20-min tasks, the greedy approach places the low-priority tasks first, potentially
blocking the high-priority task. An exact solver (ILP or branch-and-bound) would
find the best overall assignment but would be too slow for interactive use.

Recommendation: For small daily task sets (< 20 tasks), greedy is acceptable.
For larger or more complex scenarios, consider local-search improvements
(e.g., swapping adjacent tasks) or a more sophisticated heuristic.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used for:

- Rapid design iteration (UML/mermaid diagrams and class responsibilities).
- Scaffolding dataclasses and method signatures.
- Implementing and refactoring scheduler logic and helpers.
- Generating unit test skeletons and simple test cases.
- Drafting Streamlit session_state usage and small UI snippets.
  Helpful prompts included requests for: dataclass implementations, scheduling algorithm examples, conflict-detection helpers, Streamlit state patterns, and concise documentation.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

AI suggested implementing ScheduledTask with time only start_time and end_time fields. I initially accepted this but later realized it creates ambiguity for same day scheduling and breaks for multi day or overnight tasks. I evaluated this by:

1. Writing a test case that scheduled tasks across a day boundary.
2. Observing the logic fail silently (times were compared without dates).
3. Documenting the limitation in code comments and the reflection.
4. Deciding to defer a fix to a future iteration since the current Streamlit UI only handles single day scheduling.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Implemented unit tests and manual checks for:

- Task completion behavior (mark_complete updates completed and completed_at).
- Pet task management (adding a task increases pet's task list).
- Task ordering logic (organize_tasks sorts by priority and scheduled_time).
- Basic scheduling run via main.py to validate end-to-end behavior.
  These tests validated core invariants (state changes, ownership relationships, ordering) that the scheduler relies on.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence: Moderate for small, same day schedules and typical usage patterns. The current implementation handles most everyday cases but can fail in edge scenarios.

Next tests / edge cases:

- Tasks that span multiple availability windows.
- Many small tasks that fragment windows and block higher-priority tasks.
- Recurrence across changes and multi-day schedules.
- Performance/stress tests with large numbers of tasks and windows.
- Integration tests involving Streamlit session state persistence.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the separation of concerns between data models and scheduler logic, clear dataclass definitions, Streamlit session_state integration for persistence, and having unit tests to validate critical behaviors.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would improve the following:

- Switch ScheduledTask to full datetimes (start/end) and add timezone awareness.
- Replace greedy algorithm with a hybrid heuristic or use local search / small ILP for better packing.
- Add persistent storage (SQLite or simple JSON) and proper authentication with hashed passwords.
- Expand test coverage and add property-based tests for schedule validity.
- Improve UI to show task/schedule conflicts visually, add drag-and-drop task reordering, display reasoning for each scheduled task placement, and support multi-day schedule views.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned how to design iteratively using AI while always validating suggestions with tests, small manual runs, and testing the app incrementally to make sure that I am satisfied with the changes being made.
