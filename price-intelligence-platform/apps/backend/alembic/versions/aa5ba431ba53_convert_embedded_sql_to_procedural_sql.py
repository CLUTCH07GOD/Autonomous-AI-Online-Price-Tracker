"""convert_embedded_sql_to_procedural_sql

Revision ID: aa5ba431ba53
Revises: 6f63e51ca389
Create Date: 2026-05-22 19:55:02.596924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa5ba431ba53'
down_revision: Union[str, None] = '6f63e51ca389'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create v_category_volatility_heatmap view
    op.execute("""
    CREATE OR REPLACE VIEW v_category_volatility_heatmap AS
    SELECT 
        COALESCE(p.category, 'Uncategorized') AS category,
        DATE(ph.captured_at) AS date,
        AVG(ph.price) AS avg_price,
        COUNT(ph.id) AS count
    FROM products p
    JOIN price_history ph ON ph.product_id = p.id
    GROUP BY p.category, DATE(ph.captured_at)
    """)

    # 2. Create v_category_analytics view
    op.execute("""
    CREATE OR REPLACE VIEW v_category_analytics AS
    SELECT 
        COALESCE(p.category, 'Uncategorized') AS category,
        COUNT(p.id) AS products,
        COALESCE(AVG(p.current_best_price), 0) AS average_price
    FROM products p
    GROUP BY p.category
    """)

    # 3. Create get_retailer_comparison stored procedure
    op.execute("DROP PROCEDURE IF EXISTS get_retailer_comparison")
    op.execute("""
    CREATE PROCEDURE get_retailer_comparison(IN p_product_id INT)
    BEGIN
        SELECT 
            website_id,
            MIN(price) AS lowest_price,
            AVG(price) AS average_price
        FROM competitor_prices
        WHERE product_id = p_product_id
        GROUP BY website_id;
    END
    """)

    # 4. Create get_dashboard_metrics stored procedure
    op.execute("DROP PROCEDURE IF EXISTS get_dashboard_metrics")
    op.execute("""
    CREATE PROCEDURE get_dashboard_metrics()
    BEGIN
        DECLARE v_total_products INT;
        DECLARE v_active_alerts INT;
        DECLARE v_price_drops_24h INT;
        DECLARE v_total_savings DECIMAL(12,2);

        SELECT COUNT(*) INTO v_total_products FROM products;

        SELECT COUNT(*) INTO v_active_alerts FROM alerts WHERE is_active = 1;

        SELECT COUNT(*) INTO v_price_drops_24h
        FROM products p
        WHERE p.current_best_price IS NOT NULL
          AND p.current_best_price < (
            SELECT ph.price
            FROM price_history ph
            WHERE ph.product_id = p.id
              AND ph.captured_at < UTC_TIMESTAMP() - INTERVAL 24 HOUR
            ORDER BY ph.captured_at DESC
            LIMIT 1
          );

        SELECT COALESCE(SUM(mrp - current_best_price), 0) INTO v_total_savings
        FROM products
        WHERE mrp IS NOT NULL
          AND current_best_price IS NOT NULL
          AND mrp > current_best_price;

        SELECT v_total_products AS total_products,
               v_active_alerts AS active_alerts,
               v_price_drops_24h AS price_drops_24h,
               v_total_savings AS total_savings;
    END
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_category_volatility_heatmap")
    op.execute("DROP VIEW IF EXISTS v_category_analytics")
    op.execute("DROP PROCEDURE IF EXISTS get_retailer_comparison")
    op.execute("DROP PROCEDURE IF EXISTS get_dashboard_metrics")
