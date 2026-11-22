
"""Task execution metrics for MeshWeaver."""

from dataclasses import dataclass


@dataclass
class TaskMetrics:
    submitted: int = 0
    successful: int = 0
    failed: int = 0
    retries: int = 0
    timeouts: int = 0
    total_duration: float = 0.0

    def record_submission(self):
        self.submitted += 1

    def record_success(self, duration):
        self.successful += 1
        self.total_duration += duration

    def record_failure(self, duration):
        self.failed += 1
        self.total_duration += duration

    def record_retry(self):
        self.retries += 1

    def record_timeout(self):
        self.timeouts += 1

    def snapshot(self):
        completed = self.successful + self.failed

        average = (
            self.total_duration / completed
            if completed else 0.0
        )

        success_rate = (
            self.successful / completed * 100
            if completed else 0.0
        )

        return {
            "submitted": self.submitted,
            "successful": self.successful,
            "failed": self.failed,
            "pending": self.submitted - completed,
            "retries": self.retries,
            "timeouts": self.timeouts,
            "average_duration": round(average, 6),
            "success_rate": round(success_rate, 2),
        }
