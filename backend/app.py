"""
app.py
Build a few jobs, register them, run them, print a summary.
"""


from models import EmailJob, DataProcessingJob, PriorityJob

from task_manager import TaskManager

from executor import Executor


def build_jobs():
    jobs = [
        EmailJob(1, "user@example.com"),
        DataProcessingJob(2, "dataset_A"),
        PriorityJob(3, "Critical security alert", 10),
        EmailJob(4, "admin@example.com"),
        DataProcessingJob(5, "dataset_B"),
        PriorityJob(6, "Urgent system backup", 8),
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