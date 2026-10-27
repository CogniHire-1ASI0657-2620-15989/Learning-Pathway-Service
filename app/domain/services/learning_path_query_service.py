from abc import ABC, abstractmethod

from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.queries.get_learning_path_by_job_query import GetLearningPathByJobQuery
from app.domain.model.queries.get_learning_path_progress_query import GetLearningPathProgressQuery


class LearningPathQueryService(ABC):
    @abstractmethod
    async def handle_get_by_job(self, query: GetLearningPathByJobQuery) -> LearningPath | None: ...

    @abstractmethod
    async def handle_get_progress(self, query: GetLearningPathProgressQuery) -> LearningPath | None: ...
