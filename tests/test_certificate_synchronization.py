from datetime import UTC, datetime

import pytest

from app.application.internal.command_services.default_certificate_command_service import DefaultCertificateCommandService
from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.entities.certificate import Certificate
from app.domain.model.value_objects.certificate_status import CertificateStatus
from app.domain.model.value_objects.certificate_synchronization_status import CertificateSynchronizationStatus
from app.domain.model.value_objects.learning_path_status import LearningPathStatus


NOW = datetime(2026, 10, 27, tzinfo=UTC)


class InMemoryCertificateRepository:
    def __init__(self, certificate: Certificate) -> None:
        self.certificate = certificate

    async def upsert(self, certificate: Certificate) -> Certificate:
        self.certificate = certificate
        return certificate

    async def find_by_id_and_user(self, certificate_id: int, user_id: int) -> Certificate | None:
        if self.certificate.id == certificate_id and self.certificate.user_id == user_id:
            return self.certificate
        return None


class InMemoryLearningPathRepository:
    def __init__(self, learning_path: LearningPath) -> None:
        self.learning_path = learning_path

    async def find_by_id_and_user(self, learning_path_id: int, user_id: int) -> LearningPath | None:
        if self.learning_path.id == learning_path_id and self.learning_path.user_id == user_id:
            return self.learning_path
        return None


class FakeIdentitySkillClient:
    def __init__(self) -> None:
        self.calls: list[tuple[int, str]] = []

    async def ensure_verified_hard_skill(self, user_id: int, skill_name: str) -> None:
        self.calls.append((user_id, skill_name))


class FakeGapAnalysisClient:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int]] = []

    async def regenerate_report(self, user_id: int, job_id: int) -> None:
        self.calls.append((user_id, job_id))


def approved_certificate() -> Certificate:
    return Certificate(
        id=3,
        user_id=7,
        learning_path_id=1,
        skill_name="SQL",
        provider="Udemy",
        original_filename="sql.pdf",
        content_type="application/pdf",
        content=b"certificate",
        content_sha256="hash",
        status=CertificateStatus.APPROVED,
        extracted_text="Ana Perez SQL Udemy",
        detected_name="Ana Perez",
        detected_course_title="SQL",
        detected_provider="Udemy",
        validation_detail="Validated.",
        profile_sync_status=CertificateSynchronizationStatus.PENDING,
        gap_refresh_status=CertificateSynchronizationStatus.PENDING,
        synchronization_detail=None,
        profile_synced_at=None,
        gap_refreshed_at=None,
        created_at=NOW,
        updated_at=NOW,
    )


def learning_path() -> LearningPath:
    return LearningPath(
        id=1,
        user_id=7,
        job_id=44,
        gap_report_id=9,
        gap_report_updated_at=NOW,
        status=LearningPathStatus.ACTIVE,
        progress_percentage=0,
        created_at=NOW,
        updated_at=NOW,
    )


@pytest.mark.asyncio
async def test_approved_certificate_promotes_skill_and_regenerates_gap_report() -> None:
    certificate_repository = InMemoryCertificateRepository(approved_certificate())
    identity_client = FakeIdentitySkillClient()
    gap_client = FakeGapAnalysisClient()
    commits = 0

    async def commit() -> None:
        nonlocal commits
        commits += 1

    service = DefaultCertificateCommandService(
        validation_service=None,
        certificate_repository=certificate_repository,
        learning_path_repository=InMemoryLearningPathRepository(learning_path()),
        identity_skill_client=identity_client,
        gap_analysis_client=gap_client,
        commit=commit,
    )

    synchronized = await service.handle_synchronize(user_id=7, certificate_id=3)
    repeated = await service.handle_synchronize(user_id=7, certificate_id=3)

    assert synchronized.profile_sync_status == CertificateSynchronizationStatus.SYNCHRONIZED
    assert synchronized.gap_refresh_status == CertificateSynchronizationStatus.SYNCHRONIZED
    assert identity_client.calls == [(7, "SQL")]
    assert gap_client.calls == [(7, 44)]
    assert repeated is synchronized
    assert commits == 2


@pytest.mark.asyncio
async def test_non_approved_certificate_does_not_change_profile_or_gap_report() -> None:
    certificate = approved_certificate()
    certificate.status = CertificateStatus.COURSE_MISMATCH
    certificate.profile_sync_status = CertificateSynchronizationStatus.NOT_REQUIRED
    certificate.gap_refresh_status = CertificateSynchronizationStatus.NOT_REQUIRED
    certificate_repository = InMemoryCertificateRepository(certificate)
    identity_client = FakeIdentitySkillClient()
    gap_client = FakeGapAnalysisClient()

    async def commit() -> None:
        return None

    service = DefaultCertificateCommandService(
        validation_service=None,
        certificate_repository=certificate_repository,
        learning_path_repository=InMemoryLearningPathRepository(learning_path()),
        identity_skill_client=identity_client,
        gap_analysis_client=gap_client,
        commit=commit,
    )

    unchanged = await service.handle_synchronize(user_id=7, certificate_id=3)

    assert unchanged.status == CertificateStatus.COURSE_MISMATCH
    assert identity_client.calls == []
    assert gap_client.calls == []
