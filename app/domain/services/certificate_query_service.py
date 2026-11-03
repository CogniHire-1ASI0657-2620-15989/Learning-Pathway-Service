from abc import ABC, abstractmethod

from app.domain.model.entities.certificate import Certificate
from app.domain.model.queries.get_certificate_by_id_query import GetCertificateByIdQuery
from app.domain.model.queries.list_certificates_query import ListCertificatesQuery


class CertificateQueryService(ABC):
    @abstractmethod
    async def handle_get_by_id(self, query: GetCertificateByIdQuery) -> Certificate | None: ...

    @abstractmethod
    async def handle_list(self, query: ListCertificatesQuery) -> list[Certificate]: ...
