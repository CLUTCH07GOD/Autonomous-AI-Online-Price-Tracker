import { AlertRecord, ComparisonResult, DashboardMetrics, DiscountAnalysis, HealthStatus, HeatmapCell, NotificationRecord, Prediction, Product, ProductHistory, Recommendation, TrendRecord } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";
const REQUEST_TIMEOUT_MS = 8000;
const SCRAPER_TIMEOUT_MS = 45000;
const RETRYABLE_STATUS = new Set([408, 429, 500, 502, 503, 504]);

let token = localStorage.getItem("price_intelligence_token") || "";
type ApiRequestInit = RequestInit & { timeoutMs?: number };

function delay(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function request<T>(path: string, options: ApiRequestInit = {}, retries = 2): Promise<T> {
  const url = `${API_BASE}${path}`;
  const method = options.method || "GET";
  const controller = new AbortController();
  const { timeoutMs = REQUEST_TIMEOUT_MS, ...fetchOptions } = options;
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  let response: Response;
  console.log(`[API] ${method} ${url}`);
  try {
    response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...fetchOptions.headers,
      },
    });
  } catch (error) {
    window.clearTimeout(timeout);
    console.error(`[API] Network failure for ${url}`, error);
    if (retries > 0) {
      await delay(350 * 2 ** (2 - retries));
      return request<T>(path, options, retries - 1);
    }
    throw new Error(error instanceof DOMException && error.name === "AbortError" ? "Request timed out" : "Unable to reach backend");
  } finally {
    window.clearTimeout(timeout);
  }

  if (!response.ok) {
    console.error(`[API] Error ${response.status} from ${url}`);
    
    if (response.status === 401 && !path.startsWith("/auth/")) {
      await login();
      return request<T>(path, options, 0);
    }

    if (RETRYABLE_STATUS.has(response.status) && retries > 0) {
      await delay(350 * 2 ** (2 - retries));
      return request<T>(path, options, retries - 1);
    }

    let errorMsg = `Request failed with ${response.status}`;
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorData.message || JSON.stringify(errorData);
      if (Array.isArray(errorData.detail)) {
        errorMsg = errorData.detail.map((d: any) => d.msg).join(", ");
      }
    } catch {
      errorMsg = await response.text() || errorMsg;
    }
    console.error(`[API] Error details:`, errorMsg);
    throw new Error(errorMsg);
  }
  try {
    const data = await response.json();
    return data as T;
  } catch {
    return undefined as T;
  }
}

export async function login(email = "demo@price.ai", password = "password123") {
  const data = await request<{ access_token: string }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  token = data.access_token;
  localStorage.setItem("price_intelligence_token", token);
}

export async function register(name: string, email: string, password: string) {
  const data = await request<{ access_token: string }>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
  token = data.access_token;
  localStorage.setItem("price_intelligence_token", token);
}

export const api = {
  health: () => request<HealthStatus>("/health", {}, 1),
  dashboard: () => request<DashboardMetrics>("/analytics/dashboard"),
  me: () => request<any>("/auth/me"),
  products: () => request<Product[]>("/products"),
  addProduct: (url: string, target_price?: number) =>
    request<Product>("/products", { method: "POST", body: JSON.stringify({ url, target_price }), timeoutMs: SCRAPER_TIMEOUT_MS }, 0),
  refreshProduct: (id: number) => request<Product>(`/products/${id}/refresh`, { method: "POST", timeoutMs: SCRAPER_TIMEOUT_MS }, 0),
  deleteProduct: (id: number) => request<{ status: string }>(`/products/${id}`, { method: "DELETE" }),
  predictions: () => request<Prediction[]>("/predictions"),
  predict: (id: number) => request<Prediction>(`/predictions/${id}`, { method: "POST" }),
  predictStandard: (id: number) => request<Prediction[]>(`/predictions/${id}/standard`, { method: "POST" }),
  comparisons: (q = "") => request<ComparisonResult[]>(`/comparisons?q=${encodeURIComponent(q)}`),
  productHistory: (productId?: number) => request<ProductHistory>(`/analytics/history${productId ? `?product_id=${productId}` : ""}`),
  categoryAnalytics: () => request<any[]>("/analytics/category"),
  alerts: () => request<AlertRecord[]>("/alerts"),
  createAlert: (product_id: number, target_price: number, channel_email = true, channel_telegram = false, percentage_drop?: number, price_lowest_in_x_days?: number) =>
    request<AlertRecord>("/alerts", { method: "POST", body: JSON.stringify({ product_id, target_price, channel_email, channel_telegram, percentage_drop, price_lowest_in_x_days }) }),
  toggleAlert: (id: number) => request<AlertRecord>(`/alerts/${id}/toggle`, { method: "PATCH" }),
  notifications: () => request<NotificationRecord[]>("/alerts/notifications"),
  heatmap: () => request<HeatmapCell[]>("/intelligence/heatmap"),
  recommendations: () => request<Recommendation[]>("/intelligence/recommendations"),
  discount: (id: number) => request<DiscountAnalysis>(`/intelligence/discounts/${id}`, { method: "POST" }),
  discounts: () => request<DiscountAnalysis[]>("/intelligence/discounts"),
  trend: (id: number) => request<TrendRecord>(`/intelligence/trends/${id}`, { method: "POST" }),
  trends: () => request<TrendRecord[]>("/intelligence/trends"),
  retailers: (id: number) => request<any[]>(`/intelligence/retailers/${id}`),
  automation: () => request<any>("/intelligence/automation/status"),
  preferences: () => request<any>("/settings/preferences"),
  updatePreferences: (payload: any) => request<any>("/settings/preferences", { method: "PUT", body: JSON.stringify(payload) }),
  references: () => request<any[]>("/intelligence/references"),
  parseReference: (raw_text: string, locale_hint: string) =>
    request<any>("/intelligence/references/parse", { method: "POST", body: JSON.stringify({ raw_text, locale_hint }) }),
};
