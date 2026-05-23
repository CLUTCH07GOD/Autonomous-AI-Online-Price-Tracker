"""align strong schema procedures and triggers

Revision ID: 0003_align_strong_schema_procedures
Revises: aa5ba431ba53
Create Date: 2026-05-22
"""

from alembic import op

revision = "0003_align_strong_schema_procedures"
down_revision = "aa5ba431ba53"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
        CREATE OR REPLACE VIEW v_category_volatility_heatmap AS
        SELECT
            COALESCE(p.category, 'Uncategorized') AS category,
            DATE(ph.captured_at) AS date,
            AVG(ph.price) AS avg_price,
            COUNT(ph.id) AS count
        FROM products p
        JOIN price_history ph ON ph.product_id = p.id
        GROUP BY p.category, DATE(ph.captured_at)
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW v_category_analytics AS
        SELECT
            COALESCE(p.category, 'Uncategorized') AS category,
            COUNT(p.id) AS products,
            COALESCE(AVG(p.current_best_price), 0) AS average_price
        FROM products p
        GROUP BY p.category
        """
    )

    op.execute("DROP TRIGGER IF EXISTS trg_price_history_alert_audit")
    op.execute("DROP TRIGGER IF EXISTS trg_price_history_audit")
    op.execute(
        """
        CREATE TRIGGER trg_price_history_audit
        AFTER INSERT ON price_history
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_logs(entity_type, entity_id, action, after_state, created_at)
            VALUES('price_history', NEW.id, 'insert',
                   JSON_OBJECT('product_id', NEW.product_id, 'price', NEW.price), NOW());
        END
        """
    )

    op.execute("DROP TRIGGER IF EXISTS trg_price_history_update_product")
    op.execute(
        """
        CREATE TRIGGER trg_price_history_update_product
        AFTER INSERT ON price_history
        FOR EACH ROW
        BEGIN
            UPDATE products
            SET current_best_price = CASE
                    WHEN current_best_price IS NULL THEN NEW.price
                    WHEN NEW.price < current_best_price THEN NEW.price
                    ELSE current_best_price
                END,
                lowest_price = CASE
                    WHEN lowest_price IS NULL THEN NEW.price
                    WHEN NEW.price < lowest_price THEN NEW.price
                    ELSE lowest_price
                END,
                highest_price = CASE
                    WHEN highest_price IS NULL THEN NEW.price
                    WHEN NEW.price > highest_price THEN NEW.price
                    ELSE highest_price
                END,
                updated_at = NOW()
            WHERE id = NEW.product_id;
        END
        """
    )

    op.execute("DROP PROCEDURE IF EXISTS refresh_price_daily_analytics")
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

    op.execute("DROP PROCEDURE IF EXISTS get_retailer_comparison")
    op.execute(
        """
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
        """
    )

    op.execute("DROP PROCEDURE IF EXISTS get_dashboard_metrics")
    op.execute(
        """
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
        """
    )

    op.execute("DROP PROCEDURE IF EXISTS upsert_product")
    op.execute(
        """
        CREATE PROCEDURE upsert_product(
            IN p_owner_id INT,
            IN p_title VARCHAR(500),
            IN p_brand VARCHAR(160),
            IN p_category VARCHAR(160),
            IN p_image_url TEXT,
            IN p_currency VARCHAR(8),
            IN p_mrp DECIMAL(12,2)
        )
        BEGIN
            DECLARE v_product_id INT;

            SELECT id INTO v_product_id
            FROM products
            WHERE title = p_title AND COALESCE(brand, '') = COALESCE(p_brand, '')
            LIMIT 1;

            IF v_product_id IS NULL THEN
                INSERT INTO products(owner_id, title, brand, category, image_url, currency, mrp)
                VALUES(p_owner_id, p_title, p_brand, p_category, p_image_url, COALESCE(p_currency, 'INR'), p_mrp);
                SET v_product_id = LAST_INSERT_ID();
            ELSE
                UPDATE products
                SET owner_id = COALESCE(p_owner_id, owner_id),
                    image_url = COALESCE(p_image_url, image_url),
                    mrp = COALESCE(p_mrp, mrp),
                    updated_at = NOW()
                WHERE id = v_product_id;
            END IF;

            SELECT v_product_id AS product_id;
        END
        """
    )

    op.execute("DROP PROCEDURE IF EXISTS record_price_snapshot")
    op.execute(
        """
        CREATE PROCEDURE record_price_snapshot(
            IN p_product_id INT,
            IN p_product_link_id INT,
            IN p_website_id INT,
            IN p_price DECIMAL(12,2),
            IN p_mrp DECIMAL(12,2),
            IN p_availability VARCHAR(80)
        )
        BEGIN
            INSERT INTO price_history(product_id, product_link_id, website_id, price, mrp, availability)
            VALUES(p_product_id, p_product_link_id, p_website_id, p_price, p_mrp, p_availability);

            UPDATE product_links
            SET last_price = p_price,
                availability = p_availability,
                last_checked_at = NOW(),
                scrape_status = 'SUCCESS',
                error_message = NULL
            WHERE id = p_product_link_id;
        END
        """
    )

    op.execute("DROP PROCEDURE IF EXISTS log_scrape_result")
    op.execute(
        """
        CREATE PROCEDURE log_scrape_result(
            IN p_product_link_id INT,
            IN p_website_id INT,
            IN p_status VARCHAR(40),
            IN p_http_status INT,
            IN p_latency_ms INT,
            IN p_retry_count INT,
            IN p_error_message TEXT
        )
        BEGIN
            INSERT INTO scraper_logs(product_link_id, website_id, status, http_status, latency_ms, retry_count, error_message)
            VALUES(p_product_link_id, p_website_id, p_status, p_http_status, p_latency_ms, p_retry_count, p_error_message);

            UPDATE product_links
            SET scrape_status = p_status,
                error_message = p_error_message,
                last_checked_at = NOW()
            WHERE id = p_product_link_id;
        END
        """
    )

    op.execute("DROP PROCEDURE IF EXISTS create_alert")
    op.execute(
        """
        CREATE PROCEDURE create_alert(
            IN p_user_id INT,
            IN p_product_id INT,
            IN p_target_price DECIMAL(12,2),
            IN p_percentage_drop DECIMAL(5,2),
            IN p_lowest_in_days INT,
            IN p_channel_email TINYINT(1),
            IN p_channel_telegram TINYINT(1),
            IN p_priority VARCHAR(24)
        )
        BEGIN
            INSERT INTO alerts(user_id, product_id, target_price, percentage_drop, price_lowest_in_x_days,
                               channel_email, channel_telegram, priority)
            VALUES(p_user_id, p_product_id, p_target_price, p_percentage_drop, p_lowest_in_days,
                   COALESCE(p_channel_email, 1), COALESCE(p_channel_telegram, 0), COALESCE(p_priority, 'normal'));
        END
        """
    )

    op.execute("DROP PROCEDURE IF EXISTS get_price_trend")
    op.execute(
        """
        CREATE PROCEDURE get_price_trend(
            IN p_product_id INT,
            IN p_days INT
        )
        BEGIN
            SELECT
                DATE(captured_at) AS date,
                MIN(price) AS min_price,
                MAX(price) AS max_price,
                AVG(price) AS avg_price,
                COUNT(*) AS samples
            FROM price_history
            WHERE product_id = p_product_id
              AND captured_at >= UTC_TIMESTAMP() - INTERVAL p_days DAY
            GROUP BY DATE(captured_at)
            ORDER BY DATE(captured_at);
        END
        """
    )


def downgrade() -> None:
    op.execute("DROP PROCEDURE IF EXISTS get_price_trend")
    op.execute("DROP PROCEDURE IF EXISTS create_alert")
    op.execute("DROP PROCEDURE IF EXISTS log_scrape_result")
    op.execute("DROP PROCEDURE IF EXISTS record_price_snapshot")
    op.execute("DROP PROCEDURE IF EXISTS upsert_product")
    op.execute("DROP PROCEDURE IF EXISTS get_dashboard_metrics")
    op.execute("DROP PROCEDURE IF EXISTS get_retailer_comparison")
    op.execute("DROP PROCEDURE IF EXISTS refresh_price_daily_analytics")
    op.execute("DROP TRIGGER IF EXISTS trg_price_history_update_product")
    op.execute("DROP TRIGGER IF EXISTS trg_price_history_audit")
    op.execute("DROP VIEW IF EXISTS v_category_analytics")
    op.execute("DROP VIEW IF EXISTS v_category_volatility_heatmap")
    op.execute("DROP VIEW IF EXISTS v_product_price_intelligence")
