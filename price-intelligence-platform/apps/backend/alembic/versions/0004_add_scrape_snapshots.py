"""add scrape snapshots

Revision ID: 0004_add_scrape_snapshots
Revises: 0003_align_strong_schema_procedures
Create Date: 2026-05-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_add_scrape_snapshots"
down_revision = "0003_align_strong_schema_procedures"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scrape_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_link_id", sa.Integer(), sa.ForeignKey("product_links.id", ondelete="SET NULL"), nullable=True),
        sa.Column("website_id", sa.Integer(), sa.ForeignKey("websites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("raw_html", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scrape_snapshots_status", "scrape_snapshots", ["status"])
    op.create_index("ix_scrape_snapshots_scraped_at", "scrape_snapshots", ["scraped_at"])


def downgrade() -> None:
    op.drop_index("ix_scrape_snapshots_scraped_at", table_name="scrape_snapshots")
    op.drop_index("ix_scrape_snapshots_status", table_name="scrape_snapshots")
    op.drop_table("scrape_snapshots")
