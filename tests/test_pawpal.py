import pytest
from datetime import datetime

from pawpal_system import Task, Pet


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
