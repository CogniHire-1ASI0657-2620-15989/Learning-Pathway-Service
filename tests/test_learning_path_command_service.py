from datetime import UTC, datetime

import pytest

from app.application.internal.command_services.default_learning_path_command_service import DefaultLearningPathCommandService
from app.application.internal.command_services.default_learning_path_recommendation_service import (
    LearningPathRecommendation,
    VideoRecommendation,
)
from app.application.ports.youtube_video_search_client import YouTubeVideo
from app.domain.model.commands.generate_learning_path_command import GenerateLearningPathCommand
from app.domain.model.commands.mark_learning_path_item_watched_command import MarkLearningPathItemWatchedCommand
from app.domain.model.value_objects.learning_path_item_status import LearningPathItemStatus


NOW = datetime(2026, 10, 27, tzinfo=UTC)


class FakeRecommendationService:
    def __init__(self) -> None:
        self.calls = 0

    async def recommend(self, user_id: int, job_id: int) -> LearningPathRecommendation:
        self.calls += 1
        assert (user_id, job_id) == (7, 44)
        return LearningPathRecommendation(
            gap_report_id=9,
            gap_report_updated_at=NOW,
            recommendations=[
                VideoRecommendation(
                    position=1,
                    skill_name="SQL",
                    skill_type="hard",
                    video=YouTubeVideo(
                        video_id="sql-video",
                        title="SQL desde cero",
                        channel_title="Canal SQL",
                        description=None,
                        url="https://www.youtube.com/watch?v=sql-video",
                        thumbnail_url=None,
                    ),
                )
            ],
        )


class InMemoryLearningPathRepository:
    def __init__(self) -> None:
        self.learning_path = None

    async def find_by_user_and_job(self, user_id: int, job_id: int):
        if self.learning_path and (self.learning_path.user_id, self.learning_path.job_id) == (user_id, job_id):
            return self.learning_path
        return None

    async def find_by_id_and_user(self, learning_path_id: int, user_id: int):
        if self.learning_path and (self.learning_path.id, self.learning_path.user_id) == (learning_path_id, user_id):
            return self.learning_path
        return None

    async def upsert(self, learning_path):
        if learning_path.id is None:
            learning_path.id = 1
            for index, item in enumerate(learning_path.items, start=1):
                item.id = index
                item.learning_path_id = learning_path.id
        self.learning_path = learning_path
        return learning_path


@pytest.mark.asyncio
async def test_generates_once_and_preserves_an_existing_learning_path() -> None:
    recommender = FakeRecommendationService()
    repository = InMemoryLearningPathRepository()
    commits = 0

    async def commit() -> None:
        nonlocal commits
        commits += 1

    service = DefaultLearningPathCommandService(recommender, repository, commit)

    first = await service.handle_generate(GenerateLearningPathCommand(user_id=7, job_id=44))
    second = await service.handle_generate(GenerateLearningPathCommand(user_id=7, job_id=44))

    assert first.id == 1
    assert first.gap_report_id == 9
    assert first.items[0].status == LearningPathItemStatus.PENDING
    assert second is first
    assert recommender.calls == 1
    assert commits == 1


@pytest.mark.asyncio
async def test_marks_a_video_as_watched_and_updates_progress() -> None:
    recommender = FakeRecommendationService()
    repository = InMemoryLearningPathRepository()

    async def commit() -> None:
        return None

    service = DefaultLearningPathCommandService(recommender, repository, commit)
    learning_path = await service.handle_generate(GenerateLearningPathCommand(user_id=7, job_id=44))

    updated = await service.handle_mark_item_watched(
        MarkLearningPathItemWatchedCommand(user_id=7, learning_path_id=learning_path.id, item_id=learning_path.items[0].id)
    )

    assert updated.items[0].status == LearningPathItemStatus.WATCHED
    assert updated.progress_percentage == 100
    assert updated.status.value == "completed"
