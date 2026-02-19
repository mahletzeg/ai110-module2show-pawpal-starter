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

    # Add tasks out of chronological order to test sorting/filtering
    today = datetime.now().date()

    # Create several tasks with explicit scheduled times (and one unscheduled)
    t_a_late = Task(task_id="t1", description="Morning feeding", task_type="feeding", duration=15, priority=5,
                    pet_id=pet_a.pet_id, created_by=owner.owner_id,
                    scheduled_time=datetime.combine(today, time(8, 30)))

    t_b_mid = Task(task_id="t2", description="Short play", task_type="play", duration=10, priority=3,
                   pet_id=pet_b.pet_id, created_by=owner.owner_id,
                   scheduled_time=datetime.combine(today, time(8, 45)))

    t_a_early = Task(task_id="t3", description="Quick meds", task_type="medication", duration=10, priority=5,
                     pet_id=pet_a.pet_id, created_by=owner.owner_id,
                     scheduled_time=datetime.combine(today, time(8, 15)))

    t_unscheduled = Task(task_id="t4", description="Grooming prep", task_type="grooming", duration=20, priority=2,
                         pet_id=pet_b.pet_id, created_by=owner.owner_id)

    t_evening = Task(task_id="t5", description="Evening walk", task_type="walk", duration=30, priority=4,
                     pet_id=pet_b.pet_id, created_by=owner.owner_id,
                     scheduled_time=datetime.combine(today, time(17, 0)))

    # Add tasks to pets in an intentionally scrambled order
    owner.add_task_to_pet(pet_b.pet_id, t_b_mid)
    owner.add_task_to_pet(pet_a.pet_id, t_a_early)
    owner.add_task_to_pet(pet_b.pet_id, t_unscheduled)
    owner.add_task_to_pet(pet_a.pet_id, t_a_late)
    owner.add_task_to_pet(pet_b.pet_id, t_evening)

    # Add two tasks that intentionally overlap (same start time) to trigger conflict detection.
    t_conflict1 = Task(task_id="t6", description="Conflict A", task_type="check", duration=20, priority=3,
                       pet_id=pet_a.pet_id, created_by=owner.owner_id,
                       scheduled_time=datetime.combine(today, time(9, 0)))
    t_conflict2 = Task(task_id="t7", description="Conflict B", task_type="check", duration=20, priority=3,
                       pet_id=pet_b.pet_id, created_by=owner.owner_id,
                       scheduled_time=datetime.combine(today, time(9, 0)))

    owner.add_task_to_pet(pet_a.pet_id, t_conflict1)
    owner.add_task_to_pet(pet_b.pet_id, t_conflict2)

    # Mark one task complete to test completed filtering
    next_task = t_b_mid.mark_complete()
    if next_task:
        # attach the generated next-occurrence task to the same pet
        owner.add_task_to_pet(pet_b.pet_id, next_task)

    # Run simple checks: unsorted, sorted, filtered by pet name, exclude completed
    scheduler = Scheduler()

    print("\nAll collected tasks (unsorted, include completed):")
    all_tasks = scheduler.collect_tasks(owner, include_completed=True)
    for t in all_tasks:
        sched = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "unscheduled"
        print(f"- {t.task_id}: pet={t.pet_id}, time={sched}, completed={t.completed}, priority={t.priority}")

    print("\nOrganized (sorted) tasks:")
    organized = scheduler.organize_tasks(all_tasks)
    for t in organized:
        sched = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "unscheduled"
        print(f"- {t.task_id}: {sched} | {t.get_summary()}")

    print("\nFiltered by pet name 'Fluffy':")
    fluffy_tasks = scheduler.collect_tasks(owner, include_completed=True, pet_name="Fluffy")
    for t in fluffy_tasks:
        sched = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "unscheduled"
        print(f"- {t.task_id}: pet=Fluffy, time={sched}, completed={t.completed}")

    print("\nCollected excluding completed tasks:")
    not_completed = scheduler.collect_tasks(owner, include_completed=False)
    for t in not_completed:
        sched = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "unscheduled"
        print(f"- {t.task_id}: pet={t.pet_id}, time={sched}, completed={t.completed}")

    # Finally, generate the day's schedule and print it
    plan = scheduler.schedule_tasks(owner, datetime.now())
    print("\nGenerated DailyCarePlan schedule:\n")
    if not plan.scheduled_tasks:
        print("  No tasks scheduled.")
        return

    pet_map = {p.pet_id: p for p in owner.pets}
    for st in plan.scheduled_tasks:
        pet_name = pet_map.get(st.task.pet_id).name if st.task.pet_id in pet_map else st.task.pet_id
        time_slot = f"{pretty_time(st.start_time)}-{pretty_time(st.end_time)}"
        print(f"  {time_slot:>12} | {pet_name:8} | {st.task.get_summary():45} | {st.reasoning}")

    # Check for lightweight conflict warnings and print them
    warnings = scheduler.get_conflict_warnings(plan)
    if warnings:
        print("\nScheduler warnings:")
        for w in warnings:
            print(f"- {w}")
    else:
        print("\nNo conflicts detected.")


if __name__ == "__main__":
    main()
