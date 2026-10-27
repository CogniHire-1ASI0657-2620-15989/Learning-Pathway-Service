from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.value_objects.learning_path_item_status import LearningPathItemStatus
from app.interfaces.rest.resources.learning_path_resource import (
    LearningPathItemResource,
    LearningPathProgressResource,
    LearningPathResource,
)


class LearningPathResourceFromEntityAssembler:
    @staticmethod
    def to_resource(learning_path: LearningPath) -> LearningPathResource:
        return LearningPathResource(
            id=learning_path.id,
            job_id=learning_path.job_id,
            gap_report_id=learning_path.gap_report_id,
            status=learning_path.status.value,
            progress_percentage=learning_path.progress_percentage,
            created_at=learning_path.created_at,
            updated_at=learning_path.updated_at,
            items=[
                LearningPathItemResource(
                    id=item.id,
                    position=item.position,
                    skill_name=item.skill_name,
                    skill_type=item.skill_type,
                    youtube_video_id=item.youtube_video_id,
                    video_title=item.video_title,
                    channel_title=item.channel_title,
                    video_description=item.video_description,
                    video_url=item.video_url,
                    thumbnail_url=item.thumbnail_url,
                    status=item.status.value,
                    watched_at=item.watched_at,
                )
                for item in learning_path.items
            ],
        )

    @staticmethod
    def to_progress_resource(learning_path: LearningPath) -> LearningPathProgressResource:
        watched_items = sum(item.status == LearningPathItemStatus.WATCHED for item in learning_path.items)
        return LearningPathProgressResource(
            learning_path_id=learning_path.id,
            status=learning_path.status.value,
            progress_percentage=learning_path.progress_percentage,
            total_items=len(learning_path.items),
            watched_items=watched_items,
        )
