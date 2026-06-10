"""Add product sellers and discounts.

Revision ID: 003_product_sellers_discounts
Revises: 002_shop_api
Create Date: 2026-06-10 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "003_product_sellers_discounts"
down_revision: str | None = "002_shop_api"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("discount_percent", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("products", sa.Column("seller_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_products_seller_id"), "products", ["seller_id"], unique=False)

    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.create_check_constraint(
            "ck_products_discount",
            "products",
            "discount_percent BETWEEN 0 AND 100",
        )
        op.create_foreign_key(
            "fk_products_seller_id_users",
            "products",
            "users",
            ["seller_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.drop_constraint("fk_products_seller_id_users", "products", type_="foreignkey")
        op.drop_constraint("ck_products_discount", "products", type_="check")
    op.drop_index(op.f("ix_products_seller_id"), table_name="products")
    op.drop_column("products", "seller_id")
    op.drop_column("products", "discount_percent")
