from datetime import datetime, time

from pawpal_system import Owner, Pet, Task, TimeWindow, Scheduler


def pretty_time(t: time) -> str:
    return t.strftime("%H:%M")


def main():
    # Create owner and availability
    owner = Owner(owner_id="owner1", name="Alex")
    owner.availability.append(TimeWindow(window_id="morn", start_time=time(8, 0), end_time=time(10, 0)))
    owner.availability.append(TimeWindow(window_id="eve", start_time=time(17, 0), end_time=time(19, 0)))

    # Create two pets
    pet_a = Pet(pet_id="petA", name="Fluffy", category="cat")
    pet_b = Pet(pet_id="petB", name="Max", category="dog")
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    # Add tasks to pets (different durations and priorities)
    t1 = Task(task_id="t1", description="Morning feeding", task_type="feeding", duration=15, priority=5, pet_id=pet_a.pet_id, created_by=owner.owner_id)
    t2 = Task(task_id="t2", description="Walk around block", task_type="walk", duration=30, priority=4, pet_id=pet_b.pet_id, created_by=owner.owner_id)
    t3 = Task(task_id="t3", description="Give meds", task_type="medication", duration=10, priority=5, pet_id=pet_a.pet_id, created_by=owner.owner_id)

    owner.add_task_to_pet(pet_a.pet_id, t1)
    owner.add_task_to_pet(pet_b.pet_id, t2)
    owner.add_task_to_pet(pet_a.pet_id, t3)

    # Run scheduler
    scheduler = Scheduler()
    plan = scheduler.schedule_tasks(owner, datetime.now())

    # Print today's schedule
    print("Today's Schedule:\n")
    if not plan.scheduled_tasks:
        print("  No tasks scheduled.")
        return

    # helper to map pet ids
    pet_map = {p.pet_id: p for p in owner.pets}

    for st in plan.scheduled_tasks:
        pet_name = pet_map.get(st.task.pet_id).name if st.task.pet_id in pet_map else st.task.pet_id
        print(f"- {pretty_time(st.start_time)} - {pretty_time(st.end_time)} | {pet_name} | {st.task.get_summary()} | {st.reasoning}")


if __name__ == "__main__":
    main()
