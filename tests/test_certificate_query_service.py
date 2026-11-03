import pytest

from app.application.internal.query_service.default_certificate_query_service import DefaultCertificateQueryService
from app.domain.model.queries.list_certificates_query import ListCertificatesQuery


class FakeCertificateRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int | None]] = []

    async def list_by_user(self, user_id: int, learning_path_id: int | None = None) -> list[str]:
        self.calls.append((user_id, learning_path_id))
        return ["certificate"]


@pytest.mark.asyncio
async def test_lists_only_the_current_users_certificates_for_a_learning_path() -> None:
    repository = FakeCertificateRepository()
    service = DefaultCertificateQueryService(repository)

    certificates = await service.handle_list(ListCertificatesQuery(user_id=7, learning_path_id=2))

    assert certificates == ["certificate"]
    assert repository.calls == [(7, 2)]
