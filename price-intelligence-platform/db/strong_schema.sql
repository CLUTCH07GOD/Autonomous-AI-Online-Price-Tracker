-- Strong MySQL schema + procedural SQL for Price Intelligence Platform.
-- Designed to be run on a fresh database.

CREATE DATABASE IF NOT EXISTS price_intelligence
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE price_intelligence;

-- Core reference tables.
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(160) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(40) NOT NULL DEFAULT 'user',
  telegram_chat_id VARCHAR(80) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS websites (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(80) NOT NULL UNIQUE,
  base_url VARCHAR(255) NOT NULL,
  adapter_key VARCHAR(80) NOT NULL UNIQUE,
  enabled TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(160) NOT NULL UNIQUE,
  parent_id INT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_categories_parent
    FOREIGN KEY (parent_id) REFERENCES categories(id)
    ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS brands (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(160) NOT NULL UNIQUE,
  normalized_name VARCHAR(160) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  owner_id INT NULL,
  category_id INT NULL,
  brand_id INT NULL,
  title VARCHAR(500) NOT NULL,
  brand VARCHAR(160) NULL,
  category VARCHAR(160) NULL,
  image_url TEXT NULL,
  currency VARCHAR(8) NOT NULL DEFAULT 'INR',
  current_best_price DECIMAL(12,2) NULL,
  mrp DECIMAL(12,2) NULL,
  rating DECIMAL(4,2) NULL,
  rating_count INT NOT NULL DEFAULT 0,
  lowest_price DECIMAL(12,2) NULL,
  highest_price DECIMAL(12,2) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_products_owner
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_products_category
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
  CONSTRAINT fk_products_brand
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX ix_products_title ON products(title);
CREATE INDEX ix_products_category_brand ON products(category_id, brand_id);

CREATE TABLE IF NOT EXISTS product_links (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  website_id INT NOT NULL,
  url TEXT NOT NULL,
  sku VARCHAR(160) NULL,
  last_price DECIMAL(12,2) NULL,
  availability VARCHAR(80) NULL,
  last_checked_at DATETIME NULL,
  scrape_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
  error_message TEXT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  CONSTRAINT fk_product_links_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  CONSTRAINT fk_product_links_website
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX ix_product_links_product_id ON product_links(product_id);
CREATE INDEX ix_product_links_website_id ON product_links(website_id);

CREATE TABLE IF NOT EXISTS price_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  product_link_id INT NOT NULL,
  website_id INT NOT NULL,
  price DECIMAL(12,2) NOT NULL,
  mrp DECIMAL(12,2) NULL,
  availability VARCHAR(80) NULL,
  captured_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_price_history_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  CONSTRAINT fk_price_history_product_link
    FOREIGN KEY (product_link_id) REFERENCES product_links(id) ON DELETE CASCADE,
  CONSTRAINT fk_price_history_website
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX ix_price_history_product_captured ON price_history(product_id, captured_at);
CREATE INDEX ix_price_history_captured_at ON price_history(captured_at);

CREATE TABLE IF NOT EXISTS alerts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  target_price DECIMAL(12,2) NOT NULL,
  percentage_drop DECIMAL(5,2) NULL,
  price_lowest_in_x_days INT NULL,
  channel_email TINYINT(1) NOT NULL DEFAULT 1,
  channel_telegram TINYINT(1) NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  priority VARCHAR(24) NOT NULL DEFAULT 'normal',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_alerts_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_alerts_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX ix_alerts_user_active ON alerts(user_id, is_active);
CREATE INDEX ix_alerts_user_id ON alerts(user_id);
CREATE INDEX ix_alerts_product_id ON alerts(product_id);

CREATE TABLE IF NOT EXISTS ml_predictions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  model_name VARCHAR(120) NOT NULL,
  predicted_price DECIMAL(12,2) NOT NULL,
  forecast_for DATETIME NOT NULL,
  confidence DECIMAL(5,4) NULL,
  signal VARCHAR(80) NULL,
  metadata JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_predictions_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX ix_predictions_product_forecast ON ml_predictions(product_id, forecast_for);

CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NULL,
  type VARCHAR(60) NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  channel VARCHAR(40) NOT NULL,
  sent_at DATETIME NULL,
  read_at DATETIME NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notifications_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_notifications_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_preferences (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  category_id INT NULL,
  brand_id INT NULL,
  min_discount_pct DECIMAL(5,2) NOT NULL DEFAULT 10.00,
  max_budget DECIMAL(12,2) NULL,
  alert_sensitivity VARCHAR(24) NOT NULL DEFAULT 'balanced',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_user_preferences_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_user_preferences_category
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
  CONSTRAINT fk_user_preferences_brand
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX ix_user_preferences_user ON user_preferences(user_id);

CREATE TABLE IF NOT EXISTS recommendation_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  product_id INT NOT NULL,
  recommendation_type VARCHAR(80) NOT NULL,
  score DECIMAL(7,4) NOT NULL,
  reason TEXT NOT NULL,
  model_name VARCHAR(120) NULL,
  shown_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  clicked_at DATETIME NULL,
  CONSTRAINT fk_recommendation_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_recommendation_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX ix_recommendation_user_product ON recommendation_logs(user_id, product_id);
CREATE INDEX ix_recommendation_score ON recommendation_logs(score);

CREATE TABLE IF NOT EXISTS scraper_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_link_id INT NULL,
  website_id INT NULL,
  status VARCHAR(40) NOT NULL,
  http_status INT NULL,
  latency_ms INT NULL,
  retry_count INT NOT NULL DEFAULT 0,
  error_message TEXT NULL,
  scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_scraper_logs_link
    FOREIGN KEY (product_link_id) REFERENCES product_links(id) ON DELETE SET NULL,
  CONSTRAINT fk_scraper_logs_website
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX ix_scraper_logs_status ON scraper_logs(status);
CREATE INDEX ix_scraper_logs_scraped_at ON scraper_logs(scraped_at);

CREATE TABLE IF NOT EXISTS search_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  query VARCHAR(500) NOT NULL,
  filters JSON NULL,
  result_count INT NOT NULL DEFAULT 0,
  searched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_search_history_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX ix_search_history_query ON search_history(query);
CREATE INDEX ix_search_history_searched_at ON search_history(searched_at);

CREATE TABLE IF NOT EXISTS discount_analysis (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  advertised_discount_pct DECIMAL(6,2) NULL,
  real_discount_pct DECIMAL(6,2) NULL,
  inflated_mrp_score DECIMAL(6,4) NOT NULL DEFAULT 0.0000,
  is_fake_discount TINYINT(1) NOT NULL DEFAULT 0,
  confidence DECIMAL(5,4) NOT NULL DEFAULT 0.5000,
  analyzed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_discount_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX ix_discount_product_time ON discount_analysis(product_id, analyzed_at);
CREATE INDEX ix_discount_fake ON discount_analysis(is_fake_discount);

CREATE TABLE IF NOT EXISTS product_reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  website_id INT NULL,
  rating DECIMAL(4,2) NULL,
  review_count INT NOT NULL DEFAULT 0,
  sentiment_score DECIMAL(5,4) NULL,
  captured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_reviews_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  CONSTRAINT fk_reviews_website
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX ix_reviews_product_time ON product_reviews(product_id, captured_at);

CREATE TABLE IF NOT EXISTS trend_analysis (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  window VARCHAR(24) NOT NULL,
  trend_direction VARCHAR(24) NOT NULL,
  volatility_score DECIMAL(8,4) NOT NULL DEFAULT 0.0000,
  drop_probability DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
  seasonality_score DECIMAL(5,4) NOT NULL DEFAULT 0.0000,
  calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_trend_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX ix_trend_product_window ON trend_analysis(product_id, window, calculated_at);
CREATE INDEX ix_trend_direction ON trend_analysis(trend_direction);

CREATE TABLE IF NOT EXISTS competitor_prices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  website_id INT NOT NULL,
  price DECIMAL(12,2) NOT NULL,
  shipping_cost DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  availability VARCHAR(80) NULL,
  captured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_competitor_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  CONSTRAINT fk_competitor_website
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX ix_competitor_product_time ON competitor_prices(product_id, captured_at);
CREATE INDEX ix_competitor_website ON competitor_prices(website_id);

CREATE TABLE IF NOT EXISTS purchases (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  product_id INT NOT NULL,
  website_id INT NULL,
  purchase_price DECIMAL(12,2) NOT NULL,
  predicted_savings DECIMAL(12,2) NULL,
  purchased_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_purchases_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_purchases_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  CONSTRAINT fk_purchases_website
    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX ix_purchases_user_time ON purchases(user_id, purchased_at);

CREATE TABLE IF NOT EXISTS audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  actor_user_id INT NULL,
  entity_type VARCHAR(80) NOT NULL,
  entity_id INT NULL,
  action VARCHAR(80) NOT NULL,
  before_state JSON NULL,
  after_state JSON NULL,
  ip_address VARCHAR(64) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_audit_actor
    FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX ix_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX ix_audit_action ON audit_logs(action);
CREATE INDEX ix_audit_created ON audit_logs(created_at);

CREATE TABLE IF NOT EXISTS price_daily_analytics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  analytics_date DATE NOT NULL,
  min_price DECIMAL(12,2) NOT NULL,
  max_price DECIMAL(12,2) NOT NULL,
  avg_price DECIMAL(12,2) NOT NULL,
  sample_count INT NOT NULL,
  volatility_score DECIMAL(8,4) NOT NULL DEFAULT 0.0000,
  CONSTRAINT fk_price_daily_product
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  CONSTRAINT uq_price_daily_product_date UNIQUE (product_id, analytics_date)
) ENGINE=InnoDB;

CREATE INDEX ix_price_daily_date ON price_daily_analytics(analytics_date);

-- Views
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
GROUP BY p.id, p.title, p.current_best_price, p.mrp, c.name, b.name;

CREATE OR REPLACE VIEW v_category_volatility_heatmap AS
SELECT
  COALESCE(p.category, 'Uncategorized') AS category,
  DATE(ph.captured_at) AS date,
  AVG(ph.price) AS avg_price,
  COUNT(ph.id) AS count
FROM products p
JOIN price_history ph ON ph.product_id = p.id
GROUP BY p.category, DATE(ph.captured_at);

CREATE OR REPLACE VIEW v_category_analytics AS
SELECT
  COALESCE(p.category, 'Uncategorized') AS category,
  COUNT(p.id) AS products,
  COALESCE(AVG(p.current_best_price), 0) AS average_price
FROM products p
GROUP BY p.category;

-- Triggers
DROP TRIGGER IF EXISTS trg_price_history_audit;
DELIMITER $$
CREATE TRIGGER trg_price_history_audit
AFTER INSERT ON price_history
FOR EACH ROW
BEGIN
  INSERT INTO audit_logs(entity_type, entity_id, action, after_state, created_at)
  VALUES('price_history', NEW.id, 'insert',
         JSON_OBJECT('product_id', NEW.product_id, 'price', NEW.price), NOW());
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_price_history_update_product;
DELIMITER $$
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
END$$
DELIMITER ;

-- Stored procedures
DROP PROCEDURE IF EXISTS refresh_price_daily_analytics;
DELIMITER $$
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
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_retailer_comparison;
DELIMITER $$
CREATE PROCEDURE get_retailer_comparison(IN p_product_id INT)
BEGIN
  SELECT
    website_id,
    MIN(price) AS lowest_price,
    AVG(price) AS average_price
  FROM competitor_prices
  WHERE product_id = p_product_id
  GROUP BY website_id;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_dashboard_metrics;
DELIMITER $$
CREATE PROCEDURE get_dashboard_metrics()
BEGIN
  DECLARE v_total_products INT DEFAULT 0;
  DECLARE v_active_alerts INT DEFAULT 0;
  DECLARE v_price_drops_24h INT DEFAULT 0;
  DECLARE v_total_savings DECIMAL(12,2) DEFAULT 0;

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
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS upsert_product;
DELIMITER $$
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
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS record_price_snapshot;
DELIMITER $$
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
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS log_scrape_result;
DELIMITER $$
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
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS create_alert;
DELIMITER $$
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
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS get_price_trend;
DELIMITER $$
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
END$$
DELIMITER ;
