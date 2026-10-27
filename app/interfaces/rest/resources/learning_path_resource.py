from datetime import datetime

from pydantic import BaseModel


class LearningPathItemResource(BaseModel):
    id: int
    position: int
    skill_name: str
    skill_type: str
    youtube_video_id: str
    video_title: str
    channel_title: str
    video_description: str | None = None
    video_url: str
    thumbnail_url: str | None = None
    status: str
    watched_at: datetime | None = None


class LearningPathResource(BaseModel):
    id: int
    job_id: int
    gap_report_id: int
    status: str
    progress_percentage: int
    created_at: datetime
    updated_at: datetime
    items: list[LearningPathItemResource]


class LearningPathProgressResource(BaseModel):
    learning_path_id: int
    status: str
    progress_percentage: int
    total_items: int
    watched_items: int
