-- Advanced MySQL analytics helpers for the Price Intelligence Platform.

-- Product-level intelligence view is created by Alembic as v_product_price_intelligence.
SELECT * FROM v_product_price_intelligence ORDER BY price_samples DESC;

-- Category volatility heatmap source.
SELECT
  COALESCE(p.category, 'Uncategorized') AS category,
  DATE(ph.captured_at) AS price_date,
  AVG(ph.price) AS avg_price,
  (MAX(ph.price) - MIN(ph.price)) / NULLIF(AVG(ph.price), 0) AS volatility_score
FROM price_history ph
JOIN products p ON p.id = ph.product_id
GROUP BY COALESCE(p.category, 'Uncategorized'), DATE(ph.captured_at);

-- Retailer comparison.
SELECT
  cp.product_id,
  w.name AS retailer,
  MIN(cp.price + cp.shipping_cost) AS lowest_effective_price,
  AVG(cp.price + cp.shipping_cost) AS avg_effective_price
FROM competitor_prices cp
JOIN websites w ON w.id = cp.website_id
GROUP BY cp.product_id, w.name;

-- Products with suspicious discount behavior.
SELECT
  p.title,
  da.advertised_discount_pct,
  da.real_discount_pct,
  da.inflated_mrp_score,
  da.confidence
FROM discount_analysis da
JOIN products p ON p.id = da.product_id
WHERE da.is_fake_discount = TRUE
ORDER BY da.confidence DESC;
