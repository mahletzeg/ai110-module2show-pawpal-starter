# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler includes several intelligent features:

- **Smart sorting**: Tasks are organized by scheduled time, priority (highest first), and creation order for predictable ordering
- **Flexible filtering**: Collect tasks by pet, pet name (case-insensitive), or completion status
- **Recurring tasks**: Daily and weekly tasks automatically reschedule on completion, generating a new occurrence for the next interval
- **Conflict detection**: Pre-scheduling detection catches user-entered fixed-time conflicts; post-scheduling detection catches overlaps introduced by the scheduler
- **Lightweight warnings**: Conflicts are returned as human-readable warnings instead of crashing, allowing the plan to complete while flagging issues for the user
- **Optimized algorithm**: Conflict detection runs in O(n log n) time with early-exit logic, making it efficient even with many tasks

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Features

- **Sorting**: Scheduler.organize_tasks() sorts tasks by priority (high→low), then by scheduled_time, then created_at (uses Python sorted, O(n log n)).
- **Greedy scheduling**: Scheduler.schedule_tasks() fills Owner.availability windows sequentially, placing tasks in the earliest available slot that fits.
- **Conflict detection (warnings)**: Scheduler.has_time_conflict() checks scheduled-slot overlaps and prevents double-booking; conflicts are avoided/flagged rather than crashing.
- **Task completion tracking**: Task stores completed and completed_at; mark_complete() updates state for history and recurrence handling.
- **Recurrence support**: Task.next_occurrence() supports simple daily and weekly recurrence rules to compute the next occurrence.
- **Input validation**: Task.validate() enforces sensible duration and priority values and required fields.
- **Per-pet task ownership**: Pet holds a tasks: List[Task] with add_task() / remove_task() for clear ownership and lookup.
- **Owner aggregation**: Owner.get_all_tasks() collects tasks across pets for scheduling as a single work set.
- **Plan container**: DailyCarePlan is a self-contained result (contains ScheduledTask entries and referenced Pets) with get_reasoning_for_order().
- **Serialization / UI-friendly summaries**: Task.to_dict() and Task.get_summary() provide stable representations for UI and export.
- **Session persistence (UI)**: app.py stores the Owner instance in st.session_state so pets/tasks persist across Streamlit reruns.
- **Complexity notes**: sorting is O(n log n); the greedy scheduler and per-check conflict tests can be up to O(n \* w) or O(n^2) in worst case (n tasks, w windows), so consider a specialized solver for large-scale scheduling.

## Testing PawPal+

To verify the reliability and correctness of the PawPal+ scheduling system, run the test suite using:

```bash
python -m pytest
```

What the tests cover:

- **Sorting correctness**: Ensures tasks are returned in chronological order.
- **Recurrence logic**: Confirms that marking a daily task complete creates a new task for the following day.
- **Conflict detection**: Verifies that the scheduler flags duplicate or overlapping times.
- **Task completion and addition**: Checks that tasks can be marked complete and added to pets correctly.

**Confidence Level based on reliability**: 4/5 stars

The system passes all core scheduling, recurrence, and conflict detection tests. Most typical and edge cases are covered, but further testing may be needed for highly complex scenarios or unusual user inputs.
