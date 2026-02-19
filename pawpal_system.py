from __future__ import annotations

from dataclasses import dataclass, field
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

    def get_all_tasks(self) -> List[Task]:
        """Return all Tasks for all pets owned by this Owner."""
        tasks: List[Task] = []
        for p in self.pets:
            tasks.extend(p.get_tasks())
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

    def collect_tasks(self, owner: Owner) -> List[Task]:
        """Collect all tasks from an Owner's pets."""
        return owner.get_all_tasks()

    def organize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by priority, scheduled_time, then creation time."""
        # Primary sort: priority (descending), Secondary: scheduled_time (earliest first), Tertiary: created_at
        def key(t: Task):
            scheduled_ts = t.scheduled_time or datetime.max
            return (-t.priority, scheduled_ts, t.created_at)

        return sorted(tasks, key=key)

    def schedule_tasks(self, owner: Owner, date: datetime) -> DailyCarePlan:
        """Schedule owner's tasks into availability using a simple greedy algorithm."""
        plan_id = f"{owner.owner_id}-{date.date().isoformat()}"
        plan = DailyCarePlan(plan_id=plan_id, date=date, owner_id=owner.owner_id)

        tasks = self.organize_tasks(self.collect_tasks(owner))
        scheduled_count = 0

        for window in owner.availability:
            # build datetime boundaries for this date
            current = datetime.combine(date.date(), window.start_time)
            window_end = datetime.combine(date.date(), window.end_time)

            i = 0
            while i < len(tasks):
                task = tasks[i]
                # skip tasks already completed
                if task.completed:
                    i += 1
                    continue

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
                        # remove or mark as scheduled by popping from list
                        tasks.pop(i)
                        continue
                # move to next task if current doesn't fit
                i += 1

        return plan

    def has_time_conflict(self, scheduled_task: ScheduledTask, plan: DailyCarePlan) -> bool:
        """Return True if `scheduled_task` overlaps any existing task in `plan`."""
        s_start = scheduled_task.start_time
        s_end = scheduled_task.end_time
        for existing in plan.scheduled_tasks:
            e_start = existing.start_time
            e_end = existing.end_time
            # overlap check: start < other_end and end > other_start
            if (s_start < e_end) and (s_end > e_start):
                return True
        return False

# New class for scheduling logic
@dataclass
class CarePlanScheduler:
    def generate_daily_plan(self, user: User, date: datetime) -> DailyCarePlan:
        """Generate optimized schedule based on user availability and task priority"""
        pass
    
    def has_time_conflict(self, scheduled_task: ScheduledTask, plan: DailyCarePlan) -> bool:
        """Check if new task overlaps with existing ones"""
        pass