from dataclasses import dataclass, field
from datetime import datetime

from app.domain.model.entities.learning_path_item import LearningPathItem
from app.domain.model.value_objects.learning_path_item_status import LearningPathItemStatus
from app.domain.model.value_objects.learning_path_status import LearningPathStatus


@dataclass
class LearningPath:
    id: int | None
    user_id: int
    job_id: int
    gap_report_id: int
    gap_report_updated_at: datetime
    status: LearningPathStatus
    progress_percentage: int
    created_at: datetime
    updated_at: datetime
    items: list[LearningPathItem] = field(default_factory=list)

    def recalculate_progress(self, updated_at: datetime) -> None:
        total_items = len(self.items)
        watched_items = sum(item.status == LearningPathItemStatus.WATCHED for item in self.items)
        self.progress_percentage = (watched_items * 100 // total_items) if total_items else 0
        self.status = LearningPathStatus.COMPLETED if total_items and watched_items == total_items else LearningPathStatus.ACTIVE
        self.updated_at = updated_at
