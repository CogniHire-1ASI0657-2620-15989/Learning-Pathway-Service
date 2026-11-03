from app.domain.model.entities.certificate import Certificate
from app.domain.model.queries.get_certificate_by_id_query import GetCertificateByIdQuery
from app.domain.model.queries.list_certificates_query import ListCertificatesQuery
from app.domain.repositories.certificate_repository import CertificateRepository
from app.domain.services.certificate_query_service import CertificateQueryService


class DefaultCertificateQueryService(CertificateQueryService):
    def __init__(self, repository: CertificateRepository):
        self._repository = repository

    async def handle_get_by_id(self, query: GetCertificateByIdQuery) -> Certificate | None:
        return await self._repository.find_by_id_and_user(query.certificate_id, query.user_id)

    async def handle_list(self, query: ListCertificatesQuery) -> list[Certificate]:
        return await self._repository.list_by_user(query.user_id, query.learning_path_id)
