from dataclasses import dataclass
from datetime import datetime

from app.domain.model.value_objects.certificate_status import CertificateStatus


@dataclass
class Certificate:
    id: int | None
    user_id: int
    learning_path_id: int
    skill_name: str
    provider: str | None
    original_filename: str
    content_type: str
    content: bytes
    content_sha256: str
    status: CertificateStatus
    extracted_text: str | None
    detected_name: str | None
    detected_course_title: str | None
    detected_provider: str | None
    validation_detail: str | None
    created_at: datetime
    updated_at: datetime
