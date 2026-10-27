from dataclasses import dataclass
from datetime import datetime

from app.domain.model.value_objects.learning_path_item_status import LearningPathItemStatus


@dataclass
class LearningPathItem:
    id: int | None
    learning_path_id: int | None
    position: int
    skill_name: str
    skill_type: str
    youtube_video_id: str
    video_title: str
    channel_title: str
    video_description: str | None
    video_url: str
    thumbnail_url: str | None
    status: LearningPathItemStatus
    watched_at: datetime | None
    created_at: datetime
    updated_at: datetime

    def mark_as_watched(self, watched_at: datetime) -> None:
        self.status = LearningPathItemStatus.WATCHED
        self.watched_at = watched_at
        self.updated_at = watched_at
