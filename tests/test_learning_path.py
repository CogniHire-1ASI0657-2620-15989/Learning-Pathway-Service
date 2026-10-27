from datetime import UTC, datetime

from app.domain.model.aggregates.learning_path import LearningPath
from app.domain.model.entities.learning_path_item import LearningPathItem
from app.domain.model.value_objects.learning_path_item_status import LearningPathItemStatus
from app.domain.model.value_objects.learning_path_status import LearningPathStatus


NOW = datetime(2026, 10, 27, tzinfo=UTC)


def make_item(position: int, status: LearningPathItemStatus) -> LearningPathItem:
    return LearningPathItem(
        id=position,
        learning_path_id=1,
        position=position,
        skill_name="SQL",
        skill_type="hard",
        youtube_video_id=f"video-{position}",
        video_title=f"SQL video {position}",
        channel_title="PathBridge",
        video_description=None,
        video_url=f"https://www.youtube.com/watch?v=video-{position}",
        thumbnail_url=None,
        status=status,
        watched_at=NOW if status == LearningPathItemStatus.WATCHED else None,
        created_at=NOW,
        updated_at=NOW,
    )


def test_recalculates_progress_from_watched_videos() -> None:
    learning_path = LearningPath(
        id=1,
        user_id=7,
        job_id=10,
        gap_report_id=15,
        gap_report_updated_at=NOW,
        status=LearningPathStatus.ACTIVE,
        progress_percentage=0,
        created_at=NOW,
        updated_at=NOW,
        items=[
            make_item(1, LearningPathItemStatus.WATCHED),
            make_item(2, LearningPathItemStatus.WATCHED),
            make_item(3, LearningPathItemStatus.PENDING),
        ],
    )

    learning_path.recalculate_progress(NOW)

    assert learning_path.progress_percentage == 66
    assert learning_path.status == LearningPathStatus.ACTIVE


def test_completes_path_when_all_videos_are_watched() -> None:
    learning_path = LearningPath(
        id=1,
        user_id=7,
        job_id=10,
        gap_report_id=15,
        gap_report_updated_at=NOW,
        status=LearningPathStatus.ACTIVE,
        progress_percentage=0,
        created_at=NOW,
        updated_at=NOW,
        items=[
            make_item(1, LearningPathItemStatus.WATCHED),
            make_item(2, LearningPathItemStatus.WATCHED),
        ],
    )

    learning_path.recalculate_progress(NOW)

    assert learning_path.progress_percentage == 100
    assert learning_path.status == LearningPathStatus.COMPLETED
