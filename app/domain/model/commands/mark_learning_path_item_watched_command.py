from dataclasses import dataclass


@dataclass(frozen=True)
class MarkLearningPathItemWatchedCommand:
    user_id: int
    learning_path_id: int
    item_id: int
