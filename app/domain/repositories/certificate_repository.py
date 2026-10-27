from abc import ABC, abstractmethod

from app.domain.model.entities.certificate import Certificate


class CertificateRepository(ABC):
    @abstractmethod
    async def upsert(self, certificate: Certificate) -> Certificate: ...

    @abstractmethod
    async def find_by_id_and_user(self, certificate_id: int, user_id: int) -> Certificate | None: ...
