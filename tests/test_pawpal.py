import pytest
from datetime import datetime

from pawpal_system import Task, Pet
from pawpal_system import Scheduler
from datetime import timedelta


def test_task_mark_complete_changes_status():
    t = Task(task_id="t1", task_type="feeding", duration=10, priority=3, pet_id="p1", created_by="owner1")
    assert not t.completed
    assert t.completed_at is None

    t.mark_complete()

    assert t.completed is True
    assert isinstance(t.completed_at, datetime)


def test_adding_task_to_pet_increases_task_count():
    pet = Pet(pet_id="p1", name="Fluffy", category="cat")
    assert len(pet.get_tasks()) == 0

    task = Task(task_id="t2", task_type="walk", duration=20, priority=2, pet_id=pet.pet_id, created_by="owner1")
    pet.add_task(task)

    tasks = pet.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].task_id == "t2"


def test_sorting_correctness():
    scheduler = Scheduler()
    now = datetime.now()
    t1 = Task(task_id="t1", task_type="feeding", duration=10, priority=3, pet_id="p1", created_by="owner1", scheduled_time=now + timedelta(hours=2))
    t2 = Task(task_id="t2", task_type="walk", duration=20, priority=2, pet_id="p1", created_by="owner1", scheduled_time=now + timedelta(hours=1))
    t3 = Task(task_id="t3", task_type="play", duration=15, priority=5, pet_id="p1", created_by="owner1", scheduled_time=now + timedelta(hours=3))
    tasks = [t1, t2, t3]
    sorted_tasks = scheduler.organize_tasks(tasks)
    sorted_ids = [t.task_id for t in sorted_tasks]
    assert sorted_ids == ["t2", "t1", "t3"]


def test_recurrence_logic_daily():
    now = datetime.now()
    t = Task(task_id="t4", task_type="feeding", duration=10, priority=3, pet_id="p1", created_by="owner1", scheduled_time=now, frequency="daily")
    next_task = t.mark_complete()
    assert next_task is not None
    assert next_task.frequency == "daily"
    assert next_task.scheduled_time.date() == (now + timedelta(days=1)).date()
    assert next_task.task_id.startswith("t4-next-")


def test_conflict_detection():
    scheduler = Scheduler()
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    t1 = Task(task_id="t5", task_type="feeding", duration=30, priority=3, pet_id="p1", created_by="owner1", scheduled_time=now)
    t2 = Task(task_id="t6", task_type="walk", duration=30, priority=2, pet_id="p2", created_by="owner1", scheduled_time=now)
    tasks = [t1, t2]
    warnings = scheduler.find_scheduled_conflicts_among_tasks(tasks, now)
    assert any("overlap" in w for w in warnings)
