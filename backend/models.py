"""
models.py
Defines the Job hierarchy (parent + child classes).
Polymorphism: each subclass implements its own execute().
"""

import time

class Job:

    """Parent/base class shared by all job types."""

    def __init__(self, job_id: int, description: str) -> None:

        self.job_id = job_id
        self.description = description
        self.status = "pending"
        self._logs = []
        self._start_time = None
        self._end_time = None

    def add_log(self, message: str) -> None:
        self._logs.append(message)

    def get_logs(self):
        return list(self._logs)
    
    def start(self) -> None:
        self._start_time = time.time()
        self.add_log(f"Job {self.job_id} started")

    def end(self) -> None:
        self._end_time = time.time()
        self.add_log(f"Job {self.job_id} ended")
        self.add_log(f"Duration: {self.get_duration():.4} seconds")

    def get_duration(self) -> float:
        if self._start_time is not None and self._end_time is not None:
            return self._end_time - self._start_time
        return 0.0

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
        
        self.start()
        self.add_log(f"Email job {self.job_id} started")
        print(f"Sending email to {self.recipient}...")
        self.add_log(f"Email job {self.job_id} completed")
        self.end()

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

        self.start()
        self.add_log(f"Data job {self.job_id} started")
        print(f"Processing dataset {self.dataset}...")
        self.add_log(f"Data job {self.job_id} completed")
        self.end()

        # FIX (models.py): removed self.mark_done() here — same reason as EmailJob above.

class PriorityJob(Job):
    """Child class: high-priority job."""

    def __init__(self, job_id: int, description: str, priority: int) -> None:
        super().__init__(job_id, description)
        self.priority = priority

    def execute(self) -> None:
        self.start()
        self.add_log(f"Priority job {self.job_id} started")
        print(f"Executing priority job: {self.description} (priority={self.priority})...")
        self.add_log(f"Priority job {self.job_id} completed")
        self.end()

class JobFactory:
    @staticmethod
    def create_job(job_type: str, job_id: int, **kwargs):
        if job_type == "email":
            return EmailJob(job_id, kwargs["recipient"])
        if job_type == "data":
            return DataProcessingJob(job_id, kwargs["dataset"])
        if job_type == "priority":
            return PriorityJob(job_id, kwargs["description"], kwargs["priority"])
        if job_type == "retryable":
            return RetryableJob(job_id, kwargs["description"], kwargs.get("retries", 3))
        raise ValueError(f"Unknown job type: {job_type}")
    
class RetryableJob(Job):
    def __init__(self, job_id: int, description: str, retries: int = 3) -> None:
        super().__init__(job_id, description)
        self.retries = retries

    def execute(self) -> None:
        self.start()
        self.add_log(f"Retryable job {self.job_id} execution started")

    def finish_success(self, attempt: int) -> None:
        self.add_log(f"Retryable job {self.job_id} succeeded on attempt {attempt}")
        self.end()

    def finish_failure(self) -> None:
        self.add_log(f"Retryable job {self.job_id} failed after {self.retries} attempts")
        self.end()