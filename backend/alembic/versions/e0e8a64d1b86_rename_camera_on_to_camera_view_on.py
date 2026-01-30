"""rename camera_on to camera_view_on

Revision ID: e0e8a64d1b86
Revises: 3fd7de1c788e
Create Date: 2026-01-30 10:43:43.631679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0e8a64d1b86'
down_revision: Union[str, Sequence[str], None] = '3fd7de1c788e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "cart_session",
        sa.Column("camera_view_on", sa.Boolean(), server_default="false", nullable=False)
    )
    op.drop_column("cart_session", "camera_on")


def downgrade():
    op.add_column(
        "cart_session",
        sa.Column("camera_on", sa.Boolean(), server_default="false", nullable=False)
    )
    op.drop_column("cart_session", "camera_view_on")