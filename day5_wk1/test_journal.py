
from journal import Journal

# Step 1: Create a journal
journal = Journal("journal_test.jsonl")

# Step 2: Load existing tasks
tasks = journal.load()

# Step 3: Create a task
journal.write({
    "op": "task",
    "task": {
        "task_id": "T101",
        "status": "PENDING"
    }
})

# Step 4: Update task status
journal.write({
    "op": "update",
    "task_id": "T101",
    "fields": {"status": "RUNNING"}
})

# Step 5: Complete task
journal.write({
    "op": "update",
    "task_id": "T101",
    "fields": {"status": "COMPLETED"}
})

journal.close()

# Step 6: Simulate node restart
new_journal = Journal("journal_test.jsonl")
recovered_tasks = new_journal.load()

print("Recovered Tasks:", recovered_tasks)

new_journal.close()
