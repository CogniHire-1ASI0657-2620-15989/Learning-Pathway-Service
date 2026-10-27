import pytest
import respx
from httpx import Response

from app.infrastructure.clients.identity_service_client import IdentityServiceClient


@respx.mock
@pytest.mark.asyncio
async def test_promotes_verified_skill_through_identity_internal_endpoint() -> None:
    route = respx.post("http://identity:8000/api/v1/internal/users/7/verified-hard-skills").mock(
        return_value=Response(204)
    )

    await IdentityServiceClient("http://identity:8000").ensure_verified_hard_skill(7, "SQL")

    assert route.called
    assert route.calls.last.request.content == b'{"name":"SQL"}'
