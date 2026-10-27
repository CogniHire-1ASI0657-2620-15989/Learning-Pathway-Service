from abc import ABC, abstractmethod

from app.domain.model.commands.upload_certificate_command import UploadCertificateCommand
from app.domain.model.entities.certificate import Certificate


class CertificateCommandService(ABC):
    @abstractmethod
    async def handle_upload(self, command: UploadCertificateCommand) -> Certificate: ...
