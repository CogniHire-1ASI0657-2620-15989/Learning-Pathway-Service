from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.sqlalchemy.database import Base


class LearningPathModel(Base):
    __tablename__ = "learning_paths"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_learning_path_user_job"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    job_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    gap_report_id: Mapped[int] = mapped_column(Integer, nullable=False)
    gap_report_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    items: Mapped[list["LearningPathItemModel"]] = relationship(
        back_populates="learning_path",
        cascade="all, delete-orphan",
        order_by="LearningPathItemModel.position",
    )


class LearningPathItemModel(Base):
    __tablename__ = "learning_path_items"
    __table_args__ = (UniqueConstraint("learning_path_id", "position", name="uq_learning_path_item_position"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    learning_path_id: Mapped[int] = mapped_column(
        ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_type: Mapped[str] = mapped_column(String(30), nullable=False)
    youtube_video_id: Mapped[str] = mapped_column(String(100), nullable=False)
    video_title: Mapped[str] = mapped_column(String(500), nullable=False)
    channel_title: Mapped[str] = mapped_column(String(300), nullable=False)
    video_description: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048))
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    watched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    learning_path: Mapped[LearningPathModel] = relationship(back_populates="items")
