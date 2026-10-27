from dataclasses import dataclass
from datetime import datetime

from app.domain.model.value_objects.certificate_status import CertificateStatus
from app.domain.model.value_objects.certificate_synchronization_status import CertificateSynchronizationStatus


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
    profile_sync_status: CertificateSynchronizationStatus
    gap_refresh_status: CertificateSynchronizationStatus
    synchronization_detail: str | None
    profile_synced_at: datetime | None
    gap_refreshed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    def mark_profile_synchronized(self, synchronized_at: datetime) -> None:
        self.profile_sync_status = CertificateSynchronizationStatus.SYNCHRONIZED
        self.profile_synced_at = synchronized_at
        self.synchronization_detail = None
        self.updated_at = synchronized_at

    def mark_gap_refreshed(self, refreshed_at: datetime) -> None:
        self.gap_refresh_status = CertificateSynchronizationStatus.SYNCHRONIZED
        self.gap_refreshed_at = refreshed_at
        self.synchronization_detail = None
        self.updated_at = refreshed_at

    def mark_synchronization_failed(self, stage: str, detail: str, failed_at: datetime) -> None:
        if stage == "profile":
            self.profile_sync_status = CertificateSynchronizationStatus.FAILED
        else:
            self.gap_refresh_status = CertificateSynchronizationStatus.FAILED
        self.synchronization_detail = detail[:500]
        self.updated_at = failed_at
