from enum import Enum


class LearningPathItemStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WATCHED = "watched"
