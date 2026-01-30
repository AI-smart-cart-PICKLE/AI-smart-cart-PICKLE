"""add camera_view_on to cart_session

Revision ID: 5e709302d134
Revises: e0e8a64d1b86
Create Date: 2026-01-30 10:57:18.611035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e709302d134'
down_revision: Union[str, Sequence[str], None] = 'e0e8a64d1b86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "cart_session",
        sa.Column(
            "camera_view_on",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False
        )
    )


def downgrade():
    op.drop_column("cart_session", "camera_view_on")