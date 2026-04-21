"""
executor.py
Runs jobs concurrently using threads to simulate a scheduler.
- Random delay: simulates work
- Random failure: exercises exception handling
"""


import threading

import time

import random

from datetime import datetime

from typing import List

from errors import JobExecutionError

from models import Job, RetryableJob


class Executor:

    # FIX (executor.py): added 'manager' parameter so Executor can update
    # job statuses in TaskManager after each job succeeds or fails.
    # Previously Executor had no reference to manager, so statuses were never updated.
    def __init__(self, jobs: List[Job], manager) -> None:

        self.jobs = jobs

        self.manager = manager


    def _ts(self) -> str:

        return datetime.now().strftime("%H:%M:%S")


    def run_job(self, job: Job) -> None:
        try:
            print(f"[{self._ts()}] Executing job {job.job_id} ({job.description})...")

            if isinstance(job, RetryableJob):
                job.execute()
                success = False

                for attempt in range(1, job.retries + 1):
                    try:
                        job.add_log(f"Attempt {attempt} started")
                        time.sleep(random.uniform(1, 2))

                        if random.random() < 0.6 and attempt < job.retries:
                            raise JobExecutionError(job.job_id, f"Attempt {attempt} failed")

                        print(f"[{self._ts()}] Retryable job {job.job_id} succeeded on attempt {attempt}.")
                        job.finish_success(attempt)
                        self.manager.update_status(job, "completed")
                        success = True
                        break

                    except JobExecutionError as e:
                        print(f"[{self._ts()}] Error in retryable job {e.job_id}: {e}")
                        job.add_log(str(e))

                if not success:
                    job.finish_failure()
                    self.manager.update_status(job, "failed")

            else:
                time.sleep(random.uniform(1, 3))

                if random.random() < 0.2:
                    raise JobExecutionError(job.job_id)

                job.execute()
                self.manager.update_status(job, "completed")
                print(f"[{self._ts()}] Completed job {job.job_id}.")

        except JobExecutionError as e:
            self.manager.update_status(job, "failed")
            print(f"[{self._ts()}] Error in job {e.job_id}: {e}")


    def run(self) -> None:

        threads: List[threading.Thread] = []

        for job in self.jobs:

            t = threading.Thread(target=self.run_job, args=(job,))

            threads.append(t)

            t.start()


        for t in threads:

            t.join()