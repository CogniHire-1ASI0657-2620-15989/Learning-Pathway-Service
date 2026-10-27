from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.queries.get_learning_path_by_job_query import GetLearningPathByJobQuery
from app.domain.model.queries.get_learning_path_progress_query import GetLearningPathProgressQuery
from app.domain.repositories.learning_path_repository import LearningPathRepository
from app.domain.services.learning_path_query_service import LearningPathQueryService


class DefaultLearningPathQueryService(LearningPathQueryService):
    def __init__(self, repository: LearningPathRepository):
        self._repository = repository

    async def handle_get_by_job(self, query: GetLearningPathByJobQuery) -> LearningPath | None:
        return await self._repository.find_by_user_and_job(query.user_id, query.job_id)

    async def handle_get_progress(self, query: GetLearningPathProgressQuery) -> LearningPath | None:
        return await self._repository.find_by_id_and_user(query.learning_path_id, query.user_id)
