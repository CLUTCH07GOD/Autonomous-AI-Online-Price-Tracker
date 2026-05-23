"""enterprise intelligence schema

Revision ID: 0002_enterprise_intelligence
Revises: 0001_initial_schema
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_enterprise_intelligence"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(40), server_default="user", nullable=False))

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False, unique=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_categories_name", "categories", ["name"])

    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False, unique=True),
        sa.Column("normalized_name", sa.String(160), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_brands_name", "brands", ["name"])
    op.create_index("ix_brands_normalized_name", "brands", ["normalized_name"])

    op.add_column("products", sa.Column("category_id", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("brand_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_products_category_id", "products", "categories", ["category_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_products_brand_id", "products", "brands", ["brand_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_products_category_brand", "products", ["category_id", "brand_id"])

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("brand_id", sa.Integer(), sa.ForeignKey("brands.id", ondelete="SET NULL"), nullable=True),
        sa.Column("min_discount_pct", sa.Numeric(5, 2), server_default="10.00", nullable=False),
        sa.Column("max_budget", sa.Numeric(12, 2), nullable=True),
        sa.Column("alert_sensitivity", sa.String(24), server_default="balanced", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_preferences_user", "user_preferences", ["user_id"])

    op.create_table(
        "recommendation_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_type", sa.String(80), nullable=False),
        sa.Column("score", sa.Numeric(7, 4), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("model_name", sa.String(120), nullable=True),
        sa.Column("shown_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("clicked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_recommendation_user_product", "recommendation_logs", ["user_id", "product_id"])
    op.create_index("ix_recommendation_score", "recommendation_logs", ["score"])

    op.create_table(
        "scraper_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_link_id", sa.Integer(), sa.ForeignKey("product_links.id", ondelete="SET NULL"), nullable=True),
        sa.Column("website_id", sa.Integer(), sa.ForeignKey("websites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scraper_logs_status", "scraper_logs", ["status"])
    op.create_index("ix_scraper_logs_scraped_at", "scraper_logs", ["scraped_at"])

    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("query", sa.String(500), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=True),
        sa.Column("result_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("searched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_search_history_query", "search_history", ["query"])
    op.create_index("ix_search_history_searched_at", "search_history", ["searched_at"])

    op.create_table(
        "discount_analysis",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("advertised_discount_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("real_discount_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("inflated_mrp_score", sa.Numeric(6, 4), server_default="0.0000", nullable=False),
        sa.Column("is_fake_discount", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), server_default="0.5000", nullable=False),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_discount_product_time", "discount_analysis", ["product_id", "analyzed_at"])
    op.create_index("ix_discount_fake", "discount_analysis", ["is_fake_discount"])

    op.create_table(
        "product_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("website_id", sa.Integer(), sa.ForeignKey("websites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rating", sa.Numeric(4, 2), nullable=True),
        sa.Column("review_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("sentiment_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reviews_product_time", "product_reviews", ["product_id", "captured_at"])

    op.create_table(
        "trend_analysis",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("window", sa.String(24), nullable=False),
        sa.Column("trend_direction", sa.String(24), nullable=False),
        sa.Column("volatility_score", sa.Numeric(8, 4), server_default="0.0000", nullable=False),
        sa.Column("drop_probability", sa.Numeric(5, 4), server_default="0.0000", nullable=False),
        sa.Column("seasonality_score", sa.Numeric(5, 4), server_default="0.0000", nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_trend_product_window", "trend_analysis", ["product_id", "window", "calculated_at"])
    op.create_index("ix_trend_direction", "trend_analysis", ["trend_direction"])

    op.create_table(
        "competitor_prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("website_id", sa.Integer(), sa.ForeignKey("websites.id", ondelete="CASCADE"), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("shipping_cost", sa.Numeric(12, 2), server_default="0.00", nullable=False),
        sa.Column("availability", sa.String(80), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_competitor_product_time", "competitor_prices", ["product_id", "captured_at"])
    op.create_index("ix_competitor_website", "competitor_prices", ["website_id"])

    op.create_table(
        "purchases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("website_id", sa.Integer(), sa.ForeignKey("websites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("purchase_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("predicted_savings", sa.Numeric(12, 2), nullable=True),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_purchases_user_time", "purchases", ["user_id", "purchased_at"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("entity_type", sa.String(80), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("before_state", sa.JSON(), nullable=True),
        sa.Column("after_state", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_audit_action", "audit_logs", ["action"])
    op.create_index("ix_audit_created", "audit_logs", ["created_at"])

    op.create_table(
        "price_daily_analytics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("analytics_date", sa.Date(), nullable=False),
        sa.Column("min_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("max_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("avg_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.Column("volatility_score", sa.Numeric(8, 4), server_default="0.0000", nullable=False),
        sa.UniqueConstraint("product_id", "analytics_date", name="uq_price_daily_product_date"),
    )
    op.create_index("ix_price_daily_date", "price_daily_analytics", ["analytics_date"])

    op.execute(
        """
        CREATE OR REPLACE VIEW v_product_price_intelligence AS
        SELECT
            p.id AS product_id,
            p.title,
            p.current_best_price,
            p.mrp,
            c.name AS category_name,
            b.name AS brand_name,
            MIN(ph.price) AS historical_low,
            MAX(ph.price) AS historical_high,
            AVG(ph.price) AS historical_avg,
            COUNT(ph.id) AS price_samples
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN brands b ON b.id = p.brand_id
        LEFT JOIN price_history ph ON ph.product_id = p.id
        GROUP BY p.id, p.title, p.current_best_price, p.mrp, c.name, b.name
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_price_history_alert_audit
        AFTER INSERT ON price_history
        FOR EACH ROW
        INSERT INTO audit_logs(entity_type, entity_id, action, after_state, created_at)
        VALUES('price_history', NEW.id, 'insert', JSON_OBJECT('product_id', NEW.product_id, 'price', NEW.price), NOW())
        """
    )
    op.execute(
        """
        CREATE PROCEDURE refresh_price_daily_analytics()
        BEGIN
            REPLACE INTO price_daily_analytics(product_id, analytics_date, min_price, max_price, avg_price, sample_count, volatility_score)
            SELECT
                product_id,
                DATE(captured_at) AS analytics_date,
                MIN(price),
                MAX(price),
                AVG(price),
                COUNT(*),
                CASE WHEN AVG(price) = 0 THEN 0 ELSE (MAX(price) - MIN(price)) / AVG(price) END
            FROM price_history
            GROUP BY product_id, DATE(captured_at);
        END
        """
    )


def downgrade() -> None:
    op.execute("DROP PROCEDURE IF EXISTS refresh_price_daily_analytics")
    op.execute("DROP TRIGGER IF EXISTS trg_price_history_alert_audit")
    op.execute("DROP VIEW IF EXISTS v_product_price_intelligence")
    op.drop_table("price_daily_analytics")
    op.drop_table("audit_logs")
    op.drop_table("purchases")
    op.drop_table("competitor_prices")
    op.drop_table("trend_analysis")
    op.drop_table("product_reviews")
    op.drop_table("discount_analysis")
    op.drop_table("search_history")
    op.drop_table("scraper_logs")
    op.drop_table("recommendation_logs")
    op.drop_table("user_preferences")
    op.drop_constraint("fk_products_brand_id", "products", type_="foreignkey")
    op.drop_constraint("fk_products_category_id", "products", type_="foreignkey")
    op.drop_column("products", "brand_id")
    op.drop_column("products", "category_id")
    op.drop_table("brands")
    op.drop_table("categories")
    op.drop_column("users", "role")
