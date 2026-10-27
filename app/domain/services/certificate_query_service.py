from abc import ABC, abstractmethod

from app.domain.model.entities.certificate import Certificate
from app.domain.model.queries.get_certificate_by_id_query import GetCertificateByIdQuery


class CertificateQueryService(ABC):
    @abstractmethod
    async def handle_get_by_id(self, query: GetCertificateByIdQuery) -> Certificate | None: ...
