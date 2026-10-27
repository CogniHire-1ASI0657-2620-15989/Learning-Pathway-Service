from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.entities.learning_path_item import LearningPathItem
from app.domain.model.value_objects.learning_path_item_status import LearningPathItemStatus
from app.domain.model.value_objects.learning_path_status import LearningPathStatus
from app.domain.repositories.learning_path_repository import LearningPathRepository
from app.infrastructure.persistence.sqlalchemy.models.learning_path_model import LearningPathItemModel, LearningPathModel


class SQLAlchemyLearningPathRepository(LearningPathRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, learning_path: LearningPath) -> LearningPath:
        model = None
        if learning_path.id is not None:
            model = await self._get_model_by_id(learning_path.id)
        if model is None:
            model = LearningPathModel(user_id=learning_path.user_id, job_id=learning_path.job_id)
            self._session.add(model)
        self._copy_to_model(learning_path, model)
        await self._session.flush()
        return self._to_entity(model)

    async def find_by_user_and_job(self, user_id: int, job_id: int) -> LearningPath | None:
        result = await self._session.execute(
            select(LearningPathModel)
            .options(selectinload(LearningPathModel.items))
            .where(LearningPathModel.user_id == user_id, LearningPathModel.job_id == job_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_id_and_user(self, learning_path_id: int, user_id: int) -> LearningPath | None:
        result = await self._session.execute(
            select(LearningPathModel)
            .options(selectinload(LearningPathModel.items))
            .where(LearningPathModel.id == learning_path_id, LearningPathModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def _get_model_by_id(self, learning_path_id: int) -> LearningPathModel | None:
        result = await self._session.execute(
            select(LearningPathModel)
            .options(selectinload(LearningPathModel.items))
            .where(LearningPathModel.id == learning_path_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _copy_to_model(learning_path: LearningPath, model: LearningPathModel) -> None:
        model.user_id = learning_path.user_id
        model.job_id = learning_path.job_id
        model.gap_report_id = learning_path.gap_report_id
        model.gap_report_updated_at = learning_path.gap_report_updated_at
        model.status = learning_path.status.value
        model.progress_percentage = learning_path.progress_percentage
        model.created_at = learning_path.created_at
        model.updated_at = learning_path.updated_at
        existing_items = {item.id: item for item in model.items if item.id is not None}
        persisted_items: list[LearningPathItemModel] = []
        for item in learning_path.items:
            item_model = existing_items.get(item.id) if item.id is not None else None
            if item_model is None:
                item_model = LearningPathItemModel()
            item_model.position = item.position
            item_model.skill_name = item.skill_name
            item_model.skill_type = item.skill_type
            item_model.youtube_video_id = item.youtube_video_id
            item_model.video_title = item.video_title
            item_model.channel_title = item.channel_title
            item_model.video_description = item.video_description
            item_model.video_url = item.video_url
            item_model.thumbnail_url = item.thumbnail_url
            item_model.status = item.status.value
            item_model.watched_at = item.watched_at
            item_model.created_at = item.created_at
            item_model.updated_at = item.updated_at
            persisted_items.append(item_model)
        model.items[:] = persisted_items

    @staticmethod
    def _to_entity(model: LearningPathModel) -> LearningPath:
        return LearningPath(
            id=model.id,
            user_id=model.user_id,
            job_id=model.job_id,
            gap_report_id=model.gap_report_id,
            gap_report_updated_at=model.gap_report_updated_at,
            status=LearningPathStatus(model.status),
            progress_percentage=model.progress_percentage,
            created_at=model.created_at,
            updated_at=model.updated_at,
            items=[
                LearningPathItem(
                    id=item.id,
                    learning_path_id=item.learning_path_id,
                    position=item.position,
                    skill_name=item.skill_name,
                    skill_type=item.skill_type,
                    youtube_video_id=item.youtube_video_id,
                    video_title=item.video_title,
                    channel_title=item.channel_title,
                    video_description=item.video_description,
                    video_url=item.video_url,
                    thumbnail_url=item.thumbnail_url,
                    status=LearningPathItemStatus(item.status),
                    watched_at=item.watched_at,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
                for item in model.items
            ],
        )
