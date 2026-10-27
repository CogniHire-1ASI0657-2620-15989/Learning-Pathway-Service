from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateLearningPathCommand:
    user_id: int
    job_id: int
