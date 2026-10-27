"""Create learning pathway tables.

Revision ID: 20261027_02
Revises: 20261027_01
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa


revision = "20261027_02"
down_revision = "20261027_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_paths",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("gap_report_id", sa.Integer(), nullable=False),
        sa.Column("gap_report_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("progress_percentage", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "job_id", name="uq_learning_path_user_job"),
    )
    op.create_index("ix_learning_paths_user_id", "learning_paths", ["user_id"])
    op.create_index("ix_learning_paths_job_id", "learning_paths", ["job_id"])

    op.create_table(
        "learning_path_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("learning_path_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("skill_name", sa.String(length=100), nullable=False),
        sa.Column("skill_type", sa.String(length=30), nullable=False),
        sa.Column("youtube_video_id", sa.String(length=100), nullable=False),
        sa.Column("video_title", sa.String(length=500), nullable=False),
        sa.Column("channel_title", sa.String(length=300), nullable=False),
        sa.Column("video_description", sa.Text()),
        sa.Column("video_url", sa.String(length=2048), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=2048)),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("watched_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["learning_path_id"], ["learning_paths.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("learning_path_id", "position", name="uq_learning_path_item_position"),
    )
    op.create_index("ix_learning_path_items_learning_path_id", "learning_path_items", ["learning_path_id"])


def downgrade() -> None:
    op.drop_index("ix_learning_path_items_learning_path_id", table_name="learning_path_items")
    op.drop_table("learning_path_items")
    op.drop_index("ix_learning_paths_job_id", table_name="learning_paths")
    op.drop_index("ix_learning_paths_user_id", table_name="learning_paths")
    op.drop_table("learning_paths")
