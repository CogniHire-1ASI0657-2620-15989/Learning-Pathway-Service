"""Add certificate synchronization traceability.

Revision ID: 20261027_04
Revises: 20261027_03
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa


revision = "20261027_04"
down_revision = "20261027_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "certificates",
        sa.Column("profile_sync_status", sa.String(length=30), nullable=False, server_default="not_required"),
    )
    op.add_column(
        "certificates",
        sa.Column("gap_refresh_status", sa.String(length=30), nullable=False, server_default="not_required"),
    )
    op.add_column("certificates", sa.Column("synchronization_detail", sa.String(length=500)))
    op.add_column("certificates", sa.Column("profile_synced_at", sa.DateTime(timezone=True)))
    op.add_column("certificates", sa.Column("gap_refreshed_at", sa.DateTime(timezone=True)))
    op.alter_column("certificates", "profile_sync_status", server_default=None)
    op.alter_column("certificates", "gap_refresh_status", server_default=None)


def downgrade() -> None:
    op.drop_column("certificates", "gap_refreshed_at")
    op.drop_column("certificates", "profile_synced_at")
    op.drop_column("certificates", "synchronization_detail")
    op.drop_column("certificates", "gap_refresh_status")
    op.drop_column("certificates", "profile_sync_status")
