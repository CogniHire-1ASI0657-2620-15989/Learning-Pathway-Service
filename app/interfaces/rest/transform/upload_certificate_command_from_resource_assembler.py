from app.domain.model.commands.upload_certificate_command import UploadCertificateCommand
from app.interfaces.rest.resources.upload_certificate_resource import UploadCertificateResource


class UploadCertificateCommandFromResourceAssembler:
    @staticmethod
    def to_command(
        user_id: int,
        resource: UploadCertificateResource,
        original_filename: str,
        content_type: str,
        content: bytes,
    ) -> UploadCertificateCommand:
        return UploadCertificateCommand(
            user_id=user_id,
            learning_path_id=resource.learning_path_id,
            skill_name=resource.skill_name,
            provider=resource.provider,
            original_filename=original_filename,
            content_type=content_type,
            content=content,
        )
