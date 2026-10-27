"""Create certificate table.

Revision ID: 20261027_03
Revises: 20261027_02
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa


revision = "20261027_03"
down_revision = "20261027_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("learning_path_id", sa.Integer(), nullable=False),
        sa.Column("skill_name", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=150)),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("detected_name", sa.String(length=150)),
        sa.Column("detected_course_title", sa.String(length=500)),
        sa.Column("detected_provider", sa.String(length=150)),
        sa.Column("validation_detail", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["learning_path_id"], ["learning_paths.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_certificates_user_id", "certificates", ["user_id"])
    op.create_index("ix_certificates_learning_path_id", "certificates", ["learning_path_id"])


def downgrade() -> None:
    op.drop_index("ix_certificates_learning_path_id", table_name="certificates")
    op.drop_index("ix_certificates_user_id", table_name="certificates")
    op.drop_table("certificates")
