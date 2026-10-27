from datetime import datetime, timezone

from app.application.internal.command_services.default_learning_path_recommendation_service import DefaultLearningPathRecommendationService
from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.commands.generate_learning_path_command import GenerateLearningPathCommand
from app.domain.model.commands.mark_learning_path_item_watched_command import MarkLearningPathItemWatchedCommand
from app.domain.model.entities.learning_path_item import LearningPathItem
from app.domain.model.value_objects.learning_path_item_status import LearningPathItemStatus
from app.domain.model.value_objects.learning_path_status import LearningPathStatus
from app.domain.repositories.learning_path_repository import LearningPathRepository
from app.domain.services.learning_path_command_service import LearningPathCommandService


class DefaultLearningPathCommandService(LearningPathCommandService):
    def __init__(self, recommendation_service: DefaultLearningPathRecommendationService, repository: LearningPathRepository, commit):
        self._recommendation_service = recommendation_service
        self._repository = repository
        self._commit = commit

    async def handle_generate(self, command: GenerateLearningPathCommand) -> LearningPath:
        existing = await self._repository.find_by_user_and_job(command.user_id, command.job_id)
        if existing is not None:
            return existing

        recommendation = await self._recommendation_service.recommend(command.user_id, command.job_id)
        now = datetime.now(timezone.utc)
        learning_path = LearningPath(
            id=None,
            user_id=command.user_id,
            job_id=command.job_id,
            gap_report_id=recommendation.gap_report_id,
            gap_report_updated_at=recommendation.gap_report_updated_at,
            status=LearningPathStatus.ACTIVE,
            progress_percentage=0,
            created_at=now,
            updated_at=now,
            items=[
                LearningPathItem(
                    id=None,
                    learning_path_id=None,
                    position=item.position,
                    skill_name=item.skill_name,
                    skill_type=item.skill_type,
                    youtube_video_id=item.video.video_id,
                    video_title=item.video.title,
                    channel_title=item.video.channel_title,
                    video_description=item.video.description,
                    video_url=item.video.url,
                    thumbnail_url=item.video.thumbnail_url,
                    status=LearningPathItemStatus.PENDING,
                    watched_at=None,
                    created_at=now,
                    updated_at=now,
                )
                for item in recommendation.recommendations
            ],
        )
        saved = await self._repository.upsert(learning_path)
        await self._commit()
        return saved

    async def handle_mark_item_watched(self, command: MarkLearningPathItemWatchedCommand) -> LearningPath:
        learning_path = await self._repository.find_by_id_and_user(command.learning_path_id, command.user_id)
        if learning_path is None:
            raise ValueError("Learning path not found.")
        item = next((item for item in learning_path.items if item.id == command.item_id), None)
        if item is None:
            raise ValueError("Learning path item not found.")
        now = datetime.now(timezone.utc)
        item.mark_as_watched(now)
        learning_path.recalculate_progress(now)
        saved = await self._repository.upsert(learning_path)
        await self._commit()
        return saved
