from datetime import datetime, timezone
from hashlib import sha256

from app.application.internal.command_services.default_certificate_validation_service import DefaultCertificateValidationService
from app.application.ports.gap_analysis_client import GapAnalysisClient
from app.application.ports.identity_skill_client import IdentitySkillClient
from app.domain.model.commands.upload_certificate_command import UploadCertificateCommand
from app.domain.model.entities.certificate import Certificate
from app.domain.model.value_objects.certificate_status import CertificateStatus
from app.domain.model.value_objects.certificate_synchronization_status import CertificateSynchronizationStatus
from app.domain.repositories.certificate_repository import CertificateRepository
from app.domain.repositories.learning_path_repository import LearningPathRepository
from app.domain.services.certificate_command_service import CertificateCommandService


class DefaultCertificateCommandService(CertificateCommandService):
    def __init__(
        self,
        validation_service: DefaultCertificateValidationService,
        certificate_repository: CertificateRepository,
        learning_path_repository: LearningPathRepository,
        identity_skill_client: IdentitySkillClient,
        gap_analysis_client: GapAnalysisClient,
        commit,
    ):
        self._validation_service = validation_service
        self._certificate_repository = certificate_repository
        self._learning_path_repository = learning_path_repository
        self._identity_skill_client = identity_skill_client
        self._gap_analysis_client = gap_analysis_client
        self._commit = commit

    async def handle_upload(self, command: UploadCertificateCommand) -> Certificate:
        learning_path = await self._learning_path_repository.find_by_id_and_user(command.learning_path_id, command.user_id)
        if learning_path is None:
            raise ValueError("Learning path not found.")
        if not any(item.skill_name.casefold() == command.skill_name.casefold() for item in learning_path.items):
            raise ValueError("The certificate skill is not part of the learning path.")

        validation = await self._validation_service.validate(
            user_id=command.user_id,
            skill_name=command.skill_name,
            provider=command.provider,
            content=command.content,
            content_type=command.content_type,
        )
        now = datetime.now(timezone.utc)
        certificate = Certificate(
            id=None,
            user_id=command.user_id,
            learning_path_id=command.learning_path_id,
            skill_name=command.skill_name,
            provider=command.provider,
            original_filename=command.original_filename,
            content_type=command.content_type,
            content=command.content,
            content_sha256=sha256(command.content).hexdigest(),
            status=validation.status,
            extracted_text=validation.extracted_text,
            detected_name=validation.detected_name,
            detected_course_title=validation.detected_course_title,
            detected_provider=validation.detected_provider,
            validation_detail=validation.validation_detail,
            profile_sync_status=(
                CertificateSynchronizationStatus.PENDING
                if validation.status == CertificateStatus.APPROVED
                else CertificateSynchronizationStatus.NOT_REQUIRED
            ),
            gap_refresh_status=(
                CertificateSynchronizationStatus.PENDING
                if validation.status == CertificateStatus.APPROVED
                else CertificateSynchronizationStatus.NOT_REQUIRED
            ),
            synchronization_detail=None,
            profile_synced_at=None,
            gap_refreshed_at=None,
            created_at=now,
            updated_at=now,
        )
        saved = await self._certificate_repository.upsert(certificate)
        await self._commit()
        return await self._synchronize_if_approved(saved, learning_path)

    async def handle_synchronize(self, user_id: int, certificate_id: int) -> Certificate:
        certificate = await self._certificate_repository.find_by_id_and_user(certificate_id, user_id)
        if certificate is None:
            raise ValueError("Certificate not found.")
        learning_path = await self._learning_path_repository.find_by_id_and_user(certificate.learning_path_id, user_id)
        if learning_path is None:
            raise ValueError("Learning path not found.")
        return await self._synchronize_if_approved(certificate, learning_path)

    async def _synchronize_if_approved(self, certificate: Certificate, learning_path) -> Certificate:
        if certificate.status != CertificateStatus.APPROVED:
            return certificate
        if (
            certificate.profile_sync_status == CertificateSynchronizationStatus.SYNCHRONIZED
            and certificate.gap_refresh_status == CertificateSynchronizationStatus.SYNCHRONIZED
        ):
            return certificate

        now = datetime.now(timezone.utc)
        try:
            await self._identity_skill_client.ensure_verified_hard_skill(certificate.user_id, certificate.skill_name)
        except (RuntimeError, ValueError) as exc:
            certificate.mark_synchronization_failed("profile", str(exc), now)
            return await self._persist(certificate)

        certificate.mark_profile_synchronized(now)
        certificate = await self._persist(certificate)

        try:
            await self._gap_analysis_client.regenerate_report(certificate.user_id, learning_path.job_id)
        except (RuntimeError, ValueError) as exc:
            certificate.mark_synchronization_failed("gap", str(exc), datetime.now(timezone.utc))
            return await self._persist(certificate)

        certificate.mark_gap_refreshed(datetime.now(timezone.utc))
        return await self._persist(certificate)

    async def _persist(self, certificate: Certificate) -> Certificate:
        saved = await self._certificate_repository.upsert(certificate)
        await self._commit()
        return saved
