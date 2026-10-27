from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class UserProfile:
    user_id: int
    name: str


class IdentityProfileClient(ABC):
    @abstractmethod
    async def get_user_profile(self, user_id: int) -> UserProfile: ...
