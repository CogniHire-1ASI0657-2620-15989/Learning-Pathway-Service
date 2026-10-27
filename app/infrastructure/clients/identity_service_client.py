import httpx

from app.application.ports.identity_profile_client import IdentityProfileClient, UserProfile
from app.application.ports.identity_skill_client import IdentitySkillClient


class IdentityServiceClient(IdentityProfileClient, IdentitySkillClient):
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    async def get_user_profile(self, user_id: int) -> UserProfile:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
                response = await client.get(f"{self._base_url}/api/v1/internal/users/{user_id}/job-profile")
            if response.status_code == 404:
                raise ValueError("User profile not found.")
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Identity Service is unavailable.") from exc
        return UserProfile(user_id=int(body["id"]), name=str(body["name"]))

    async def ensure_verified_hard_skill(self, user_id: int, skill_name: str) -> None:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
                response = await client.post(
                    f"{self._base_url}/api/v1/internal/users/{user_id}/verified-hard-skills",
                    json={"name": skill_name},
                )
            if response.status_code == 404:
                raise ValueError("User profile not found.")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError("Identity Service is unavailable.") from exc
