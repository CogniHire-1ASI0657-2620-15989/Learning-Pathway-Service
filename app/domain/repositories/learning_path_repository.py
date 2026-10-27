from abc import ABC, abstractmethod

from app.domain.model.aggregates.learning_path import LearningPath


class LearningPathRepository(ABC):
    @abstractmethod
    async def upsert(self, learning_path: LearningPath) -> LearningPath: ...

    @abstractmethod
    async def find_by_user_and_job(self, user_id: int, job_id: int) -> LearningPath | None: ...
