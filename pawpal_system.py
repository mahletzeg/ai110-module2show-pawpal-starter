from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List

@dataclass
class TimeWindow:
    """Represents an owner's available time slot"""
    window_id: str
    start_time: time
    end_time: time
    
    def is_available(self) -> bool:
        return self.start_time < self.end_time

@dataclass
class Pet:
    """Represents a pet with details and special needs"""
    pet_id: str
    name: str
    category: str  # dog, cat, bird, etc.
    special_needs: List[str] = field(default_factory=list)
    owner_id: str = ""
    
    def get_special_needs(self) -> List[str]:
        return self.special_needs

@dataclass
class Task:
    """Represents a pet care task"""
    task_id: str
    task_type: str  # walk, feeding, medication, grooming
    duration: int  # in minutes
    priority: int  # 1-5, 5 being highest
    pet_id: str
    created_by: str  # user_id
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False
    completed_at: datetime = None
    
    def mark_complete(self) -> None:
        self.completed = True
        self.completed_at = datetime.now()
    
    def get_task_details(self) -> dict:
        return {
            "type": self.task_type,
            "duration": self.duration,
            "priority": self.priority
        }

@dataclass
class ScheduledTask:
    """Represents a task assigned to a specific time slot"""
    scheduled_task_id: str
    task: Task
    start_time: time
    end_time: time
    reasoning: str = ""
    
    def get_reasoning(self) -> str:
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
        self.scheduled_tasks.append(scheduled_task)
    
    def get_reasoning_for_order(self) -> str:
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
        self.care_plans.append(plan)
    
    def get_availability(self) -> List[TimeWindow]:
        return self.availability
    
    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)
    
    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

# New class for scheduling logic
@dataclass
class CarePlanScheduler:
    def generate_daily_plan(self, user: User, date: datetime) -> DailyCarePlan:
        """Generate optimized schedule based on user availability and task priority"""
        pass
    
    def has_time_conflict(self, scheduled_task: ScheduledTask, plan: DailyCarePlan) -> bool:
        """Check if new task overlaps with existing ones"""
        pass