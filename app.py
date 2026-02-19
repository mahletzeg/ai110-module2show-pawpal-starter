import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, TimeWindow, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

# Persist an Owner in the session so data survives reruns
if "owner" not in st.session_state:
    st.session_state["owner"] = Owner(owner_id="owner1", name=owner_name)
else:
    # keep name in sync with input field
    st.session_state["owner"].name = owner_name

owner: Owner = st.session_state["owner"]

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
priority_map = {"low": 1, "medium": 3, "high": 5}
if st.button("Add task"):
    # attach task to first pet if exists, otherwise create a pet from pet_name
    if not owner.pets:
        new_pet = Pet(pet_id=f"pet-{len(owner.pets)+1}", name=pet_name, category=species)
        owner.add_pet(new_pet)
        st.info(f"No pets found - created pet {pet_name} to attach task")

    pet = owner.pets[0]
    pval = priority_map.get(priority, 3)
    task = Task(
        task_id=f"t-{sum(len(p.tasks) for p in owner.pets)+1}",
        description=task_title,
        task_type="general",
        duration=int(duration),
        priority=pval,
        pet_id=pet.pet_id,
        created_by=owner.owner_id,
    )
    owner.add_task_to_pet(pet.pet_id, task)
    st.success(f"Added task to {pet.name}")

# show current tasks across all pets
all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks (across pets):")
    rows = [{"pet": next((p.name for p in owner.pets if p.pet_id == t.pet_id), t.pet_id), "task": t.get_summary()} for t in all_tasks]
    st.table(rows)
else:
    st.info("No tasks yet. Add one above.")

st.subheader("Owner & Pets")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("Create Pet"):
        if not any(p.name == pet_name for p in owner.pets):
            new_pet = Pet(pet_id=f"pet-{len(owner.pets)+1}", name=pet_name, category=species)
            owner.add_pet(new_pet)
            st.success(f"Added pet {pet_name}")
        else:
            st.info("Pet already exists")

with col_b:
    pet_options = [p.name for p in owner.pets]
    if pet_options:
        selected_pet_name = st.selectbox("Select pet", options=pet_options)
        selected_pet = next((p for p in owner.pets if p.name == selected_pet_name), owner.pets[0])
    else:
        st.info("No pets yet; create one")
        selected_pet = None

st.subheader("Add Task To Pet")
if st.button("Add task to selected pet"):
    if not owner.pets:
        st.warning("No pets to add tasks to; create a pet first.")
    else:
        pet = selected_pet or owner.pets[0]
        priority_map = {"low": 1, "medium": 3, "high": 5}
        pval = priority_map.get(priority, 3)
        task = Task(
            task_id=f"t-{len(pet.tasks)+1}",
            description=task_title,
            task_type="general",
            duration=int(duration),
            priority=pval,
            pet_id=pet.pet_id,
            created_by=owner.owner_id,
        )
        owner.add_task_to_pet(pet.pet_id, task)
        st.success(f"Added task to {pet.name}")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    plan = scheduler.schedule_tasks(owner, datetime.now())
    if not plan.scheduled_tasks:
        st.info("No tasks scheduled for the selected availability.")
    else:
        pet_map = {p.pet_id: p for p in owner.pets}
        rows = []
        for stask in plan.scheduled_tasks:
            pet_name = pet_map.get(stask.task.pet_id).name if stask.task.pet_id in pet_map else stask.task.pet_id
            rows.append({
                "start": stask.start_time.strftime("%H:%M"),
                "end": stask.end_time.strftime("%H:%M"),
                "pet": pet_name,
                "task": stask.task.get_summary(),
                "reason": stask.reasoning,
            })
        st.table(rows)
