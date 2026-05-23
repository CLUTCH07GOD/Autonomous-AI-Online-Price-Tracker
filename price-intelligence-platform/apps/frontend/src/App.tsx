import { useEffect, useState } from "react";
import { api } from "./lib/api";
import { Shell } from "./components/Shell";
import { AIInsights } from "./pages/AIInsights";
import { AlertsPage } from "./pages/AlertsPage";
import { ComparisonPage } from "./pages/ComparisonPage";
import { Dashboard } from "./pages/Dashboard";
import { DiscountPage } from "./pages/DiscountPage";
import { HeatmapPage } from "./pages/HeatmapPage";
import { HistoricalAnalytics } from "./pages/HistoricalAnalytics";
import { ProductSearch } from "./pages/ProductSearch";
import { RecommendationPage } from "./pages/RecommendationPage";
import { SettingsPage } from "./pages/SettingsPage";
import { LoginPage } from "./pages/LoginPage";
import { ReferenceHub } from "./pages/ReferenceHub";
import { LoadingBlock, ToastMessage, ToastStack } from "./components/Toast";
import { ThemeProvider } from "./components/ThemeProvider";
import { ThemeToggle } from "./components/ThemeToggle";
import { AuthProvider, useAuth } from "./components/AuthContext";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { AlertRecord, ComparisonResult, DashboardMetrics, DiscountAnalysis, HeatmapCell, NotificationRecord, Prediction, Product, ProductHistory, Recommendation, TrendRecord } from "./types";

function MainContent() {
  const { user, loading: authLoading } = useAuth();
  const [active, setActive] = useState("Dashboard");
  const [metrics, setMetrics] = useState<DashboardMetrics>();
  const [products, setProducts] = useState<Product[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [heatmap, setHeatmap] = useState<HeatmapCell[]>([]);
  const [history, setHistory] = useState<ProductHistory>();
  const [comparisons, setComparisons] = useState<ComparisonResult[]>([]);
  const [discounts, setDiscounts] = useState<DiscountAnalysis[]>([]);
  const [trends, setTrends] = useState<TrendRecord[]>([]);
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [notifications, setNotifications] = useState<NotificationRecord[]>([]);
  const [preferences, setPreferences] = useState<any>();
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState("");
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [query, setQuery] = useState("");
  const [target, setTarget] = useState("");
  const [selectedAlertProduct, setSelectedAlertProduct] = useState<number | "">("");
  const [percentageDrop, setPercentageDrop] = useState("");
  const [lowestDays, setLowestDays] = useState("");
  const [url, setUrl] = useState("");

  console.log("[App] State:", { user: !!user, authLoading, loading, active });

  function notify(type: ToastMessage["type"], text: string) {
    const id = Date.now();
    setToasts((items) => [...items, { id, type, text }]);
    window.setTimeout(() => setToasts((items) => items.filter((item) => item.id !== id)), 4500);
  }

  async function load() {
    if (!user) return;
    setLoading(true);
    try {
      const safe = async <T,>(task: Promise<T>, fallback: T, label: string): Promise<T> => {
        try {
          return await task;
        } catch (error) {
          console.error(`[App] Failed to load ${label}`, error);
          return fallback;
        }
      };
      const productRows = await safe(api.products(), [], "products");
      setProducts(productRows);
      
      const [metricsData, predictionRows, recRows, heatRows, historyRows, alertRows, notificationRows, discountRows, trendRows, prefRows] = await Promise.all([
        safe(api.dashboard(), { total_products: 0, active_alerts: 0, price_drops_24h: 0, total_savings: 0, average_accuracy: 0 }, "dashboard"),
        safe(api.predictions(), [], "predictions"),
        safe(api.recommendations(), [], "recommendations"),
        safe(api.heatmap(), [], "heatmap"),
        safe(api.productHistory(), { products: [], selected_product_id: null, history: [], stats: { lowest: 0, highest: 0, average: 0, samples: 0 }, volatility: 0 }, "history"),
        safe(api.alerts(), [], "alerts"),
        safe(api.notifications(), [], "notifications"),
        safe(api.discounts(), [], "discounts"),
        safe(api.trends(), [], "trends"),
        safe(api.preferences(), {}, "preferences"),
      ]);
      
      setMetrics(metricsData);
      setPredictions(predictionRows);
      setRecommendations(recRows);
      setHeatmap(heatRows);
      setHistory(historyRows);
      setAlerts(alertRows);
      setNotifications(notificationRows);
      setDiscounts(discountRows);
      setTrends(trendRows);
      setPreferences(prefRows);
    } catch (error) {
      console.error("Failed to load data:", error);
      notify("error", "Failed to sync with intelligence server");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (user) load();
  }, [user]);

  async function addProduct() {
    if (!url) return;
    setAction("track");
    try {
      const product = await api.addProduct(url);
      notify("success", `Tracking started for ${product.title}`);
      setUrl("");
      await load();
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Unable to track product");
    } finally {
      setAction("");
    }
  }

  async function refresh(id: number) {
    setAction(`refresh-${id}`);
    try {
      await api.refreshProduct(id);
      notify("success", "Price refresh completed");
      await load();
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Refresh failed");
    } finally {
      setAction("");
    }
  }

  async function deleteProduct(id: number) {
    setAction(`delete-${id}`);
    try {
      await api.deleteProduct(id);
      notify("success", "Product removed");
      setProducts((prev) => prev.filter((p) => p.id !== id));
      await load();
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Delete failed");
    } finally {
      setAction("");
    }
  }

  async function runPrediction(id: number) {
    setAction(`predict-${id}`);
    try {
      await api.predictStandard(id);
      await api.trend(id);
      notify("success", "7-day and 30-day predictions updated");
      await load();
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Prediction failed");
    } finally {
      setAction("");
    }
  }

  async function runDiscountScan(id: number) {
    setAction(`discount-${id}`);
    try {
      await api.discount(id);
      notify("success", "Discount intelligence updated");
      await load();
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Discount scan failed");
    } finally {
      setAction("");
    }
  }

  async function searchComparisons() {
    setAction("compare");
    try {
      setComparisons(await api.comparisons(query));
    } finally {
      setAction("");
    }
  }

  async function selectHistory(id: number) {
    setHistory(await api.productHistory(id));
  }

  async function createAlert() {
    if (!selectedAlertProduct || !Number(target)) {
      notify("error", "Select a product and enter a numeric target price");
      return;
    }
    await api.createAlert(selectedAlertProduct, Number(target), true, false, percentageDrop ? Number(percentageDrop) : undefined, lowestDays ? Number(lowestDays) : undefined);
    notify("success", "Smart alert created");
    setTarget("");
    setPercentageDrop("");
    setLowestDays("");
    await load();
  }

  async function toggleAlert(id: number) {
    await api.toggleAlert(id);
    await load();
  }

  async function saveSettings() {
    await api.updatePreferences(preferences);
    notify("success", "Settings saved");
    await load();
  }

  if (authLoading) return <LoadingBlock />;
  if (!user) return <LoginPage />;

  const page = loading ? (
    <LoadingBlock />
  ) : active === "Dashboard" ? (
    <Dashboard metrics={metrics} products={products} history={history} onRefresh={refresh} />
  ) : active === "Product Search" ? (
    <ProductSearch url={url} setUrl={setUrl} loading={action === "track"} products={products} onTrack={addProduct} onDelete={deleteProduct} action={action} />
  ) : active === "ML Insights" || active === "AI Insights" ? (
    <AIInsights products={products} predictions={predictions} recommendations={recommendations} heatmap={heatmap} onPredict={runPrediction} onDiscount={runDiscountScan} />
  ) : active === "Comparison" ? (
    <ComparisonPage query={query} setQuery={setQuery} rows={comparisons} onSearch={searchComparisons} />
  ) : active === "Trend Analytics" ? (
    <AIInsights products={products} predictions={predictions} recommendations={recommendations} heatmap={heatmap} onPredict={runPrediction} onDiscount={runDiscountScan} />
  ) : active === "Fake Discount Detector" ? (
    <DiscountPage products={products} rows={discounts} scanningId={Number(action.replace("discount-", "")) || undefined} onScan={runDiscountScan} />
  ) : active === "Recommendation Center" ? (
    <RecommendationPage rows={recommendations} onRefresh={load} />
  ) : active === "Price Heatmaps" ? (
    <HeatmapPage cells={heatmap} />
  ) : active === "Historical Analytics" ? (
    <HistoricalAnalytics data={history} onSelect={selectHistory} />
  ) : active === "Alerts" || active === "Smart Alerts" ? (
    <AlertsPage products={products} alerts={alerts} notifications={notifications} target={target} setTarget={setTarget} percentageDrop={percentageDrop} setPercentageDrop={setPercentageDrop} lowestDays={lowestDays} setLowestDays={setLowestDays} selected={selectedAlertProduct} setSelected={setSelectedAlertProduct} onCreate={createAlert} onToggle={toggleAlert} />
  ) : active === "Settings" ? (
    <SettingsPage preferences={preferences} setPreferences={setPreferences} onSave={saveSettings} />
  ) : active === "References" || active === "Reference Hub" ? (
    <ReferenceHub />
  ) : (
    <AIInsights products={products} predictions={predictions} recommendations={recommendations} heatmap={heatmap} onPredict={runPrediction} onDiscount={runDiscountScan} />
  );

  return (
    <>
      <ToastStack messages={toasts} onDismiss={(id) => setToasts((items) => items.filter((item) => item.id !== id))} />
      <Shell active={active} onNavigate={setActive} products={products}>{page}</Shell>
      <ThemeToggle />
    </>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <AuthProvider>
          <MainContent />
        </AuthProvider>
      </ErrorBoundary>
    </ThemeProvider>
  );
}
