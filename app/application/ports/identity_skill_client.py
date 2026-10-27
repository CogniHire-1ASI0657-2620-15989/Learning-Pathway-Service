from abc import ABC, abstractmethod


class IdentitySkillClient(ABC):
    @abstractmethod
    async def ensure_verified_hard_skill(self, user_id: int, skill_name: str) -> None: ...
