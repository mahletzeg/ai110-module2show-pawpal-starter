from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, time, timedelta
from typing import List, Optional

@dataclass
class TimeWindow:
    """Represents an owner's available time slot"""
    window_id: str
    start_time: time
    end_time: time
    
    def is_available(self) -> bool:
        """Return True when the time window has a valid start before end."""
        return self.start_time < self.end_time

@dataclass
class Pet:
    """Represents a pet with details and special needs"""
    pet_id: str
    name: str
    category: str  # dog, cat, bird, etc.
    special_needs: List[str] = field(default_factory=list)
    owner_id: str = ""
    # store tasks that belong to this pet
    tasks: List["Task"] = field(default_factory=list)

    def get_special_needs(self) -> List[str]:
        """Return the pet's special needs list."""
        return self.special_needs

    def add_task(self, task: "Task") -> None:
        """Attach a Task to this Pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a Task by id, returning True if removed."""
        for i, t in enumerate(self.tasks):
            if t.task_id == task_id:
                del self.tasks[i]
                return True
        return False

    def get_tasks(self) -> List["Task"]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

@dataclass
class Task:
    """Represents a pet care task / activity"""
    task_id: str
    description: str = ""
    task_type: str = ""  # walk, feeding, medication, grooming, etc.
    duration: int = 0  # in minutes
    priority: int = 3  # 1-5, 5 being highest
    pet_id: str = ""
    created_by: str = ""  # user_id
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_time: Optional[datetime] = None  # when the task is scheduled to start
    frequency: Optional[str] = None  # e.g. "once", "daily", "weekly"
    completed: bool = False
    completed_at: Optional[datetime] = None

    def validate(self) -> None:
        """Validate duration, priority and required fields for the Task."""
        if self.duration <= 0:
            raise ValueError("duration must be > 0")
        if not 1 <= self.priority <= 5:
            raise ValueError("priority must be between 1 and 5")
        if not self.task_type:
            raise ValueError("task_type is required")

    def mark_complete(self, at: Optional[datetime] = None) -> None:
        """Mark this task completed and set the completion timestamp."""
        self.completed = True
        self.completed_at = at or datetime.now()

        # For recurring tasks, we do not mutate this Task further; instead,
        # callers can examine the returned Task (if any) to add the next occurrence.
        return self._create_next_if_recurring()

    def _create_next_if_recurring(self) -> Optional["Task"]:
        """If this Task is recurring (daily/weekly), return a new Task scheduled
        for the next occurrence. Otherwise return None.

        The caller is responsible for persisting/attaching the returned Task.
        """
        if not self.frequency or self.frequency in ("", "once"):
            return None
        if self.frequency not in ("daily", "weekly"):
            return None

        # Need a base scheduled_time to compute the next occurrence
        base = self.scheduled_time or self.completed_at
        if not base:
            return None

        # Compute next occurrence using the same logic as next_occurrence
        after = self.completed_at or datetime.now()
        next_dt = self.next_occurrence(after=after)
        if not next_dt:
            # fallback: add one interval to base
            if self.frequency == "daily":
                next_dt = base + timedelta(days=1)
            elif self.frequency == "weekly":
                next_dt = base + timedelta(weeks=1)

        if not next_dt:
            return None

        # Create a new Task instance for the next occurrence
        new_task = Task(
            task_id=f"{self.task_id}-next-{next_dt.date().isoformat()}",
            description=self.description,
            task_type=self.task_type,
            duration=self.duration,
            priority=self.priority,
            pet_id=self.pet_id,
            created_by=self.created_by,
            created_at=datetime.now(),
            scheduled_time=next_dt,
            frequency=self.frequency,
            completed=False,
            completed_at=None,
        )
        return new_task

    def is_overdue(self, now: Optional[datetime] = None) -> bool:
        """Return True when the scheduled end time passed and task is not complete."""
        if self.completed or not self.scheduled_time:
            return False
        now = now or datetime.now()
        end_time = self.scheduled_time + timedelta(minutes=self.duration)
        return end_time < now

    def next_occurrence(self, after: Optional[datetime] = None) -> Optional[datetime]:
        """Return the next occurrence datetime based on `frequency` rules."""
        if not self.scheduled_time:
            return None
        after = after or datetime.now()
        if self.frequency in (None, "once", ""):
            return self.scheduled_time if (not self.completed and self.scheduled_time >= after) else None

        current = self.scheduled_time
        while current < after:
            if self.frequency == "daily":
                current += timedelta(days=1)
            elif self.frequency == "weekly":
                current += timedelta(weeks=1)
            else:
                # Unknown frequency -> treat as one-time
                return None
        return current if not self.completed else None

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation of this Task."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "task_type": self.task_type,
            "duration": self.duration,
            "priority": self.priority,
            "pet_id": self.pet_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "frequency": self.frequency,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def get_summary(self) -> str:
        """Return a short human-readable summary for UI or logs."""
        desc = f": {self.description}" if self.description else ""
        return f"{self.task_type.capitalize()}{desc} ({self.duration}m) - priority {self.priority}"

@dataclass
class ScheduledTask:
    """Represents a task assigned to a specific time slot"""
    scheduled_task_id: str
    task: Task
    start_time: time
    end_time: time
    reasoning: str = ""
    
    def get_reasoning(self) -> str:
        """Return the scheduler reasoning associated with this ScheduledTask."""
        return self.reasoning

@dataclass
class DailyCarePlan:
    """Represents an optimized daily schedule"""
    plan_id: str
    date: datetime
    owner_id: str
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_scheduled_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a ScheduledTask to this DailyCarePlan."""
        self.scheduled_tasks.append(scheduled_task)
    
    def get_reasoning_for_order(self) -> str:
        """Return a combined reasoning string explaining the task order."""
        reasons = [f"{task.reasoning}" for task in self.scheduled_tasks]
        return " | ".join(reasons)

@dataclass
class User:
    """Represents an app user"""
    user_id: str
    name: str
    email: str
    password: str  # In production, store hashed passwords
    availability: List[TimeWindow] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    care_plans: List[DailyCarePlan] = field(default_factory=list)
    
    def add_care_plan(self, plan: DailyCarePlan) -> None:
        """Attach a DailyCarePlan to this User's history."""
        self.care_plans.append(plan)
    
    def get_availability(self) -> List[TimeWindow]:
        """Return this user's availability time windows."""
        return self.availability
    
    def add_pet(self, pet: Pet) -> None:
        """Attach a Pet to this User."""
        self.pets.append(pet)
    
    def add_task(self, task: Task) -> None:
        """Add a Task to this User's loose task list."""
        self.tasks.append(task)


@dataclass
class Owner:
    """Represents an owner who manages multiple pets and has availability windows."""
    owner_id: str
    name: str
    email: str = ""
    availability: List[TimeWindow] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to the Owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self, pet_id: Optional[str] = None, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Return all Tasks for pets owned by this Owner.

        Optional filters:
        - pet_id: only tasks for the specified pet id
        - pet_name: only tasks for pets matching this name (case-insensitive)
        - completed: if set, filter by completion status (True/False). If None, return both.
        """
        tasks: List[Task] = []
        for p in self.pets:
            if pet_id is not None and p.pet_id != pet_id:
                continue
            if pet_name is not None and p.name.lower() != pet_name.lower():
                continue
            for t in p.get_tasks():
                if completed is not None and t.completed != completed:
                    continue
                tasks.append(t)
        return tasks

    def get_tasks_for_pet(self, pet_id: str) -> List[Task]:
        """Return all Tasks for a specific pet identified by `pet_id`."""
        for p in self.pets:
            if p.pet_id == pet_id:
                return p.get_tasks()
        return []

    def add_task_to_pet(self, pet_id: str, task: Task) -> bool:
        """Add a Task to the specified pet; return True if successful."""
        for p in self.pets:
            if p.pet_id == pet_id:
                p.add_task(task)
                return True
        return False


class Scheduler:
    """Core scheduling 'brain' that organizes tasks across pets for an owner."""

    def collect_tasks(self, owner: Owner, pet_id: Optional[str] = None, include_completed: bool = False, pet_name: Optional[str] = None) -> List[Task]:
        """Collect tasks from an Owner's pets with optional filtering.

        - pet_id: only collect tasks for a given pet
        - include_completed: when False (default) exclude completed tasks
        """
        completed_filter = None if include_completed else False
        return owner.get_all_tasks(pet_id=pet_id, pet_name=pet_name, completed=completed_filter)

    def organize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by scheduled time (earliest first), then priority (desc), then creation time.

        Tasks that have a scheduled_time will be ordered before unscheduled tasks for the same date.

        This implementation is robust to Task.scheduled_time being either a datetime or a time object.
        """
        def key(t: Task):
            sched = t.scheduled_time
            if sched is None:
                scheduled_ts = datetime.max
            elif isinstance(sched, datetime):
                scheduled_ts = sched
            else:
                # scheduled_time might be a time object -> combine with today's date for ordering
                scheduled_ts = datetime.combine(datetime.today(), sched)
            return (scheduled_ts, -t.priority, t.created_at)

        return sorted(tasks, key=key)

    def schedule_tasks(self, owner: Owner, date: datetime) -> DailyCarePlan:
        """Schedule owner's tasks into availability using a simple greedy algorithm.

        Improvements:
        - Respect tasks that have scheduled_time (including recurring occurrences) on the target date.
        - Filter out completed tasks by default.
        - Basic conflict detection to avoid overlaps. Any detected overlaps are returned as warnings
          on the DailyCarePlan.warnings list instead of raising exceptions.
        """
        plan_id = f"{owner.owner_id}-{date.date().isoformat()}"
        plan = DailyCarePlan(plan_id=plan_id, date=date, owner_id=owner.owner_id)

        # Build a list of candidate tasks that apply for this date.
        raw_tasks = self.collect_tasks(owner, include_completed=False)
        tasks_for_day: List[Task] = []

        day_start = datetime.combine(date.date(), time.min)
        for t in raw_tasks:
            # If task has a scheduled_time explicitly and it falls on this date -> include that occurrence
            if t.scheduled_time:
                if t.scheduled_time.date() == date.date():
                    # use a shallow copy so we don't mutate stored task objects
                    copy_task = replace(t)
                    tasks_for_day.append(copy_task)
                    continue
                # if task has frequency, check next occurrence
                if t.frequency:
                    occ = t.next_occurrence(after=day_start)
                    if occ and occ.date() == date.date():
                        copy_task = replace(t)
                        copy_task.scheduled_time = occ
                        tasks_for_day.append(copy_task)
                        continue
            else:
                # If no scheduled_time but frequency exists, check if it should occur today based on original scheduled_time
                if t.frequency and t.scheduled_time:
                    occ = t.next_occurrence(after=day_start)
                    if occ and occ.date() == date.date():
                        copy_task = replace(t)
                        copy_task.scheduled_time = occ
                        tasks_for_day.append(copy_task)
                        continue
                # otherwise include unscheduled (flexible) tasks to be fitted into windows
                tasks_for_day.append(t)
            # Before attempting to fit tasks into availability windows, detect
            # obvious conflicts among tasks that already have fixed scheduled_time
            # on the target date. These are flagged as lightweight warnings so
            # the scheduler doesn't crash but the UI can inform the user.
            pre_warnings = self.find_scheduled_conflicts_among_tasks(tasks_for_day, date)

            # Organize by scheduled time, priority, created_at
        tasks = self.organize_tasks(tasks_for_day)
        scheduled_count = 0

        for window in owner.availability:
            if not window.is_available():
                continue
            # build datetime boundaries for this date
            current = datetime.combine(date.date(), window.start_time)
            window_end = datetime.combine(date.date(), window.end_time)

            i = 0
            while i < len(tasks):
                task = tasks[i]
                # skip completed (again, defensive)
                if task.completed:
                    i += 1
                    continue

                # If task has a fixed scheduled_time for this date, attempt to place at that exact time
                if task.scheduled_time and task.scheduled_time.date() == date.date():
                    start_dt = task.scheduled_time
                    end_dt = start_dt + timedelta(minutes=task.duration)
                    # only place if within this availability window
                    if start_dt >= datetime.combine(date.date(), window.start_time) and end_dt <= window_end:
                        scheduled_task = ScheduledTask(
                            scheduled_task_id=f"{task.task_id}-{scheduled_count}",
                            task=task,
                            start_time=start_dt.time(),
                            end_time=end_dt.time(),
                            reasoning=f"Fixed time occurrence: priority {task.priority}",
                        )
                        if not self.has_time_conflict(scheduled_task, plan):
                            plan.add_scheduled_task(scheduled_task)
                            scheduled_count += 1
                            # if the fixed start is after current, advance current to the end to avoid overlapping flexible tasks
                            if start_dt >= current:
                                current = end_dt
                            # remove task from consideration
                            tasks.pop(i)
                            continue
                    # cannot place this fixed-time occurrence in this window -> skip it for this window
                    i += 1
                    continue

                # Flexible tasks: try to place at `current`
                end_time = current + timedelta(minutes=task.duration)
                if end_time <= window_end:
                    scheduled_task = ScheduledTask(
                        scheduled_task_id=f"{task.task_id}-{scheduled_count}",
                        task=task,
                        start_time=current.time(),
                        end_time=end_time.time(),
                        reasoning=f"Scheduled by Scheduler: priority {task.priority}",
                    )
                    # check conflicts within the plan
                    if not self.has_time_conflict(scheduled_task, plan):
                        plan.add_scheduled_task(scheduled_task)
                        scheduled_count += 1
                        # advance current time
                        current = end_time
                        # remove (or mark scheduled) by popping
                        tasks.pop(i)
                        continue
                # move to next task if current doesn't fit
                i += 1

        # Attach all warnings (pre-scheduling and post-scheduling conflicts)
        plan.warnings = pre_warnings + self.get_conflict_warnings(plan)
        return plan
   
    def get_conflict_warnings(self, plan: DailyCarePlan) -> List[str]:
        """Return a list of human-readable warning messages for any detected overlaps.

        This function is intentionally lightweight: it does not raise or stop execution,
        it only returns descriptive strings that the caller can display to the user.
        """
        warnings: List[str] = []
        conflicts = self.detect_conflicts(plan)
        for c in conflicts:
            if c.get("same_pet"):
                msg = (
                    f"Warning: tasks {c['task_a']} and {c['task_b']} for pet {c['pet_a']} "
                    f"overlap ({c['start_a']}-{c['end_a']} and {c['start_b']}-{c['end_b']})."
                )
            else:
                msg = (
                    f"Warning: task {c['task_a']} (pet {c['pet_a']}, {c['start_a']}-{c['end_a']}) "
                    f"overlaps with {c['task_b']} (pet {c['pet_b']}, {c['start_b']}-{c['end_b']})."
                )
            warnings.append(msg)
        return warnings

    def has_time_conflict(self, scheduled_task: ScheduledTask, plan: DailyCarePlan) -> bool:
        """Return True if `scheduled_task` overlaps any existing task in `plan`."""
        # convert to times for comparison (ScheduledTask stores time objects)
        s_start = scheduled_task.start_time
        s_end = scheduled_task.end_time
        for existing in plan.scheduled_tasks:
            e_start = existing.start_time
            e_end = existing.end_time
            # overlap check: start < other_end and end > other_start
            if (s_start < e_end) and (s_end > e_start):
                return True
        return False

    def find_conflicts_for_task(self, scheduled_task: ScheduledTask, plan: DailyCarePlan) -> List[ScheduledTask]:
        """Return a list of existing ScheduledTask objects in `plan` that overlap
        with the provided `scheduled_task`.

        This also makes it easy to see whether conflicts are with the same pet
        (by comparing `task.pet_id`).
        """
        conflicts: List[ScheduledTask] = []
        s_start = scheduled_task.start_time
        s_end = scheduled_task.end_time
        for existing in plan.scheduled_tasks:
            e_start = existing.start_time
            e_end = existing.end_time
            if (s_start < e_end) and (s_end > e_start):
                conflicts.append(existing)
        return conflicts

    def detect_conflicts(self, plan: DailyCarePlan) -> List[dict]:
        """Scan `plan` and return a list of detected overlap conflicts.

        Each conflict is a dict containing both tasks' ids, pet ids, times,
        and a boolean `same_pet` indicating whether the two tasks belong to
        the same pet.
        """
        results: List[dict] = []
        n = len(plan.scheduled_tasks)
        for i in range(n):
            a = plan.scheduled_tasks[i]
            for j in range(i + 1, n):
                b = plan.scheduled_tasks[j]
                a_start = a.start_time
                a_end = a.end_time
                b_start = b.start_time
                b_end = b.end_time
                if (a_start < b_end) and (a_end > b_start):
                    results.append({
                        "task_a": a.scheduled_task_id,
                        "task_b": b.scheduled_task_id,
                        "pet_a": a.task.pet_id,
                        "pet_b": b.task.pet_id,
                        "start_a": a_start.strftime("%H:%M"),
                        "end_a": a_end.strftime("%H:%M"),
                        "start_b": b_start.strftime("%H:%M"),
                        "end_b": b_end.strftime("%H:%M"),
                        "same_pet": a.task.pet_id == b.task.pet_id,
                    })
        return results

    def find_scheduled_conflicts_among_tasks(self, tasks: List[Task], date: datetime) -> List[str]:
        """Detect overlaps among tasks that already have fixed scheduled_time on `date`.

        Returns human-readable warning strings. This runs before scheduling and
        ensures conflicts in user-entered fixed times are reported even if the
        scheduler later shifts flexible tasks.
        
        Algorithm: Sort by start_time (O(n log n)), then scan left-to-right checking
        only potentially overlapping tasks (O(n) in typical case).
        """
        warnings: List[str] = []
        scheduled = [t for t in tasks if t.scheduled_time and t.scheduled_time.date() == date.date()]
        
        if len(scheduled) < 2:
            return warnings
        
        # Sort by start time for efficient overlap detection
        scheduled.sort(key=lambda t: t.scheduled_time)
        
        for i in range(len(scheduled)):
            a = scheduled[i]
            a_end = a.scheduled_time + timedelta(minutes=a.duration)
            
            # Only check subsequent tasks whose start_time is before a's end_time
            for j in range(i + 1, len(scheduled)):
                b = scheduled[j]
                b_start = b.scheduled_time
                
                # If b starts after a ends, no overlap possible (and all later tasks won't overlap either due to sorting)
                if b_start >= a_end:
                    break
                
                # b_start < a_end, so there's an overlap
                b_end = b_start + timedelta(minutes=b.duration)
                same = a.pet_id == b.pet_id
                if same:
                    msg = (
                        f"Warning: fixed tasks {a.task_id} and {b.task_id} for pet {a.pet_id} "
                        f"overlap ({a.scheduled_time.time().strftime('%H:%M')}-{a_end.time().strftime('%H:%M')} and "
                        f"{b_start.time().strftime('%H:%M')}-{b_end.time().strftime('%H:%M')})."
                    )
                else:
                    msg = (
                        f"Warning: fixed tasks {a.task_id} (pet {a.pet_id}) and {b.task_id} (pet {b.pet_id}) "
                        f"overlap ({a.scheduled_time.time().strftime('%H:%M')}-{a_end.time().strftime('%H:%M')} and "
                        f"{b_start.time().strftime('%H:%M')}-{b_end.time().strftime('%H:%M')})."
                    )
                warnings.append(msg)
        
        return warnings