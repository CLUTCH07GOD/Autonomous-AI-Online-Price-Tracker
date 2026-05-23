export interface Product {
  id: number;
  title: string;
  category?: string | null;
  image_url?: string | null;
  currency: string;
  current_best_price?: number | null;
  mrp?: number | null;
  rating?: number | null;
  rating_count: number;
  availability?: string | null;
  links: ProductLink[];
}

export interface ProductLink {
  id: number;
  url: string;
  last_price?: number | null;
  availability?: string | null;
  last_checked_at?: string | null;
  scrape_status?: string | null;
  error_message?: string | null;
}

export interface DashboardMetrics {
  total_products: number;
  active_alerts: number;
  price_drops_24h: number;
  total_savings: number;
  average_accuracy: number;
}

export interface ProductHistory {
  products: Array<{ id: number; title: string }>;
  selected_product_id: number | null;
  history: Array<{ price: number; captured_at: string }>;
  stats: { lowest?: number; highest?: number; average?: number; samples?: number };
  volatility: number;
}

export interface Prediction {
  id: number;
  product_id: number;
  model_name: string;
  predicted_price: number;
  forecast_for: string;
  confidence: number;
  trend: "up" | "down" | "stable";
  signal?: string | null;
}

export interface Recommendation {
  id: number;
  product_id: number;
  title: string;
  type: string;
  content: string;
  score: number;
  created_at?: string;
}

export interface HeatmapCell {
  category: string;
  date: string;
  avg_price: number;
  count: number;
}

export interface ComparisonRetailer {
  name: string;
  domain: string;
  url: string;
  price: number;
  availability?: string | null;
  in_stock: boolean;
  last_checked_at?: string | null;
}

export interface ComparisonResult {
  id: number;
  title: string;
  image_url?: string | null;
  best_price?: number | null;
  mrp?: number | null;
  currency: string;
  retailers: ComparisonRetailer[];
}

export interface AlertRecord {
  id: number;
  product_id: number;
  target_price: number;
  channel_email: boolean;
  channel_telegram: boolean;
  is_active: boolean;
  priority: string;
}

export interface NotificationRecord {
  id: number;
  product_id?: number | null;
  type: string;
  title: string;
  content: string;
  channel: string;
  created_at: string;
  read_at?: string | null;
}

export interface HealthStatus {
  status: "ok" | "degraded" | string;
  components: {
    backend: string;
    database: string;
    scraper: string;
    ml_engine: string;
  };
  version: string;
  checked_at: string;
}

export interface DiscountAnalysis {
  id: number;
  product_id: number;
  advertised_discount_pct: number;
  real_discount_pct: number;
  inflated_mrp_score: number;
  is_fake_discount: boolean;
  confidence: number;
  analyzed_at?: string;
}

export interface TrendRecord {
  id: number;
  product_id: number;
  window: string;
  trend_direction: "up" | "down" | "stable";
  volatility_score: number;
  drop_probability: number;
  seasonality_score: number;
  calculated_at?: string;
}
