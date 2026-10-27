from datetime import datetime

from pydantic import BaseModel


class CertificateResource(BaseModel):
    id: int
    learning_path_id: int
    skill_name: str
    provider: str | None = None
    original_filename: str
    content_type: str
    status: str
    detected_name: str | None = None
    detected_course_title: str | None = None
    detected_provider: str | None = None
    validation_detail: str | None = None
    created_at: datetime
    updated_at: datetime
