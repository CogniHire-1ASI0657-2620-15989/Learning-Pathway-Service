from dataclasses import dataclass


@dataclass(frozen=True)
class GetLearningPathProgressQuery:
    user_id: int
    learning_path_id: int
