from dataclasses import dataclass


@dataclass(frozen=True)
class GetLearningPathByJobQuery:
    user_id: int
    job_id: int
