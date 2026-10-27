from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.entities.certificate import Certificate
from app.domain.model.value_objects.certificate_status import CertificateStatus
from app.domain.model.value_objects.certificate_synchronization_status import CertificateSynchronizationStatus
from app.domain.repositories.certificate_repository import CertificateRepository
from app.infrastructure.persistence.sqlalchemy.models.certificate_model import CertificateModel


class SQLAlchemyCertificateRepository(CertificateRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, certificate: Certificate) -> Certificate:
        model = await self._session.get(CertificateModel, certificate.id) if certificate.id is not None else None
        if model is None:
            model = CertificateModel(user_id=certificate.user_id, learning_path_id=certificate.learning_path_id)
            self._session.add(model)
        self._copy_to_model(certificate, model)
        await self._session.flush()
        return self._to_entity(model)

    async def find_by_id_and_user(self, certificate_id: int, user_id: int) -> Certificate | None:
        model = await self._session.get(CertificateModel, certificate_id)
        if model is None or model.user_id != user_id:
            return None
        return self._to_entity(model)

    @staticmethod
    def _copy_to_model(certificate: Certificate, model: CertificateModel) -> None:
        model.user_id = certificate.user_id
        model.learning_path_id = certificate.learning_path_id
        model.skill_name = certificate.skill_name
        model.provider = certificate.provider
        model.original_filename = certificate.original_filename
        model.content_type = certificate.content_type
        model.content = certificate.content
        model.content_sha256 = certificate.content_sha256
        model.status = certificate.status.value
        model.extracted_text = certificate.extracted_text
        model.detected_name = certificate.detected_name
        model.detected_course_title = certificate.detected_course_title
        model.detected_provider = certificate.detected_provider
        model.validation_detail = certificate.validation_detail
        model.profile_sync_status = certificate.profile_sync_status.value
        model.gap_refresh_status = certificate.gap_refresh_status.value
        model.synchronization_detail = certificate.synchronization_detail
        model.profile_synced_at = certificate.profile_synced_at
        model.gap_refreshed_at = certificate.gap_refreshed_at
        model.created_at = certificate.created_at
        model.updated_at = certificate.updated_at

    @staticmethod
    def _to_entity(model: CertificateModel) -> Certificate:
        return Certificate(
            id=model.id,
            user_id=model.user_id,
            learning_path_id=model.learning_path_id,
            skill_name=model.skill_name,
            provider=model.provider,
            original_filename=model.original_filename,
            content_type=model.content_type,
            content=model.content,
            content_sha256=model.content_sha256,
            status=CertificateStatus(model.status),
            extracted_text=model.extracted_text,
            detected_name=model.detected_name,
            detected_course_title=model.detected_course_title,
            detected_provider=model.detected_provider,
            validation_detail=model.validation_detail,
            profile_sync_status=CertificateSynchronizationStatus(model.profile_sync_status),
            gap_refresh_status=CertificateSynchronizationStatus(model.gap_refresh_status),
            synchronization_detail=model.synchronization_detail,
            profile_synced_at=model.profile_synced_at,
            gap_refreshed_at=model.gap_refreshed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
