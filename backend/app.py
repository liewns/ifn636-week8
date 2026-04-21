"""
app.py
Build a few jobs, register them, run them, print a summary.
"""


from models import JobFactory, PriorityJob

from task_manager import TaskManager

from executor import Executor


def build_jobs():
    jobs = [
        JobFactory.create_job("email", 1, recipient="user@example.com"),
        JobFactory.create_job("data", 2, dataset="dataset_A"),
        JobFactory.create_job("priority", 3, description="Critical security alert", priority=10),
        JobFactory.create_job("email", 4, recipient="admin@example.com"),
        JobFactory.create_job("data", 5, dataset="dataset_B"),
        JobFactory.create_job("priority", 6, description="Urgent system backup", priority=8),
    ]

    priority_jobs = [job for job in jobs if isinstance(job, PriorityJob)]
    normal_jobs = [job for job in jobs if not isinstance(job, PriorityJob)]

    priority_jobs.sort(key=lambda job: job.priority, reverse=True)

    return priority_jobs + normal_jobs


if __name__ == "__main__":

    jobs = build_jobs()


    manager = TaskManager()

    for job in jobs:

        manager.add_job(job)  # all start as 'pending'


    # FIX (app.py): pass 'manager' to Executor so it can update statuses.
    # Previously Executor(jobs).run() had no manager reference — statuses never changed.
    Executor(jobs, manager).run()


    print("\n=== SUMMARY ===")

    print(f"Pending:   {len(manager.get_jobs_by_status('pending'))}")

    print(f"Completed: {len(manager.get_jobs_by_status('completed'))}")

    # FIX (app.py): added 'failed' count to summary so failures are visible.
    print(f"Failed:    {len(manager.get_jobs_by_status('failed'))}")

    print("\n=== LOGS ===")
    for job in jobs:
        print(f"Job {job.job_id}:")
        for log in job.get_logs():
            print(f" - {log}")