"""
models.py
Defines the Job hierarchy (parent + child classes).
Polymorphism: each subclass implements its own execute().
"""


class Job:

    """Parent/base class shared by all job types."""

    def __init__(self, job_id: int, description: str) -> None:

        self.job_id = job_id

        self.description = description

        self.status = "pending"

        self._logs = []

    def add_log(self, message: str) -> None:
        self._logs.append(message)

    def get_logs(self):
        return list(self._logs)

    def execute(self) -> None:

        """Must be overridden by subclasses."""

        raise NotImplementedError("Each job must implement its own execution logic.")

    def mark_done(self) -> None:

        self.status = "completed"


    def __repr__(self) -> str:

        return f"<Job id={self.job_id} status={self.status}desc='{self.description}'>"



class EmailJob(Job):

    """Child class: sends an email."""

    def __init__(self, job_id: int, recipient: str) -> None:

        # super() calls parent constructor (DRY)

        super().__init__(job_id, f"Send email to {recipient}")

        self.recipient = recipient


    def execute(self) -> None:
        
        self.add_log(f"Email job {self.job_id} started")

        print(f"Sending email to {self.recipient}...")

        self.add_log(f"Email job {self.job_id} completed")

        # FIX (models.py): removed self.mark_done() here.
        # Previously mark_done() set job.status="completed" inside execute(),
        # so update_status() in executor.py searched the wrong bucket and
        # added a duplicate — causing Pending:4, Completed:4 in the summary.
        # Status is now managed exclusively by TaskManager.update_status().



class DataProcessingJob(Job):

    """Child class: processes a dataset."""

    def __init__(self, job_id: int, dataset: str) -> None:

        super().__init__(job_id, f"Process dataset {dataset}")

        self.dataset = dataset


    def execute(self) -> None:

        self.add_log(f"Data job {self.job_id} started")

        print(f"Processing dataset {self.dataset}...")

        self.add_log(f"Data job {self.job_id} completed")

        # FIX (models.py): removed self.mark_done() here — same reason as EmailJob above.

class PriorityJob(Job):
    """Child class: high-priority job."""

    def __init__(self, job_id: int, description: str, priority: int) -> None:
        super().__init__(job_id, description)
        self.priority = priority

    def execute(self) -> None:

        self.add_log(f"Priority job {self.job_id} started")

        print(f"Executing priority job: {self.description} (priority={self.priority})...")

        self.add_log(f"Priority job {self.job_id} completed")