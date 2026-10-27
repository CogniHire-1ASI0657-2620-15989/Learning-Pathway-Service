from app.domain.model.entities.certificate import Certificate
from app.interfaces.rest.resources.certificate_resource import CertificateResource


class CertificateResourceFromEntityAssembler:
    @staticmethod
    def to_resource(certificate: Certificate) -> CertificateResource:
        return CertificateResource(
            id=certificate.id,
            learning_path_id=certificate.learning_path_id,
            skill_name=certificate.skill_name,
            provider=certificate.provider,
            original_filename=certificate.original_filename,
            content_type=certificate.content_type,
            status=certificate.status.value,
            detected_name=certificate.detected_name,
            detected_course_title=certificate.detected_course_title,
            detected_provider=certificate.detected_provider,
            validation_detail=certificate.validation_detail,
            profile_sync_status=certificate.profile_sync_status.value,
            gap_refresh_status=certificate.gap_refresh_status.value,
            synchronization_detail=certificate.synchronization_detail,
            profile_synced_at=certificate.profile_synced_at,
            gap_refreshed_at=certificate.gap_refreshed_at,
            created_at=certificate.created_at,
            updated_at=certificate.updated_at,
        )
