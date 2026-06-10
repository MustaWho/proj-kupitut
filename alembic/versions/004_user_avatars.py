"""Add user avatars.

Revision ID: 004_user_avatars
Revises: 003_product_sellers_discounts
Create Date: 2026-06-10 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "004_user_avatars"
down_revision: str | None = "003_product_sellers_discounts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_url")
