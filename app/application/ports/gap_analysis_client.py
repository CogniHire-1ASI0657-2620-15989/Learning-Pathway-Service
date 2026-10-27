from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MissingSkill:
    name: str
    skill_type: str


@dataclass(frozen=True)
class GapAnalysisReport:
    id: int
    job_id: int
    updated_at: datetime
    missing_hard_skills: list[MissingSkill]


class GapAnalysisClient(ABC):
    @abstractmethod
    async def get_report(self, user_id: int, job_id: int) -> GapAnalysisReport: ...

    @abstractmethod
    async def regenerate_report(self, user_id: int, job_id: int) -> GapAnalysisReport: ...
