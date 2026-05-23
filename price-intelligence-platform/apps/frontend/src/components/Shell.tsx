import { BarChart3, Bell, ChevronLeft, ChevronRight, Gauge, LineChart, LucideIcon, Search, Settings, Shuffle, History, Map, Zap, Percent, BrainCircuit, LogOut, BookOpen } from "lucide-react";
import { ReactNode, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CommandMenu } from "./CommandMenu";
import { useAuth } from "./AuthContext";
import { AmbientBackground } from "./ParticleBackground";
import { cn } from "../lib/utils";
import { api } from "../lib/api";

const nav: Array<[string, LucideIcon]> = [
  ["Dashboard", Gauge],
  ["Product Search", Search],
  ["AI Insights", BrainCircuit],
  ["Comparison", Shuffle],
  ["Trend Analytics", LineChart],
  ["Fake Discount Detector", Percent],
  ["Recommendation Center", Zap],
  ["Price Heatmaps", Map],
  ["Historical Analytics", History],
  ["Smart Alerts", Bell],
  ["Settings", Settings],
  ["References", BookOpen],
];

function ConnectionStatus() {
  const [status, setStatus] = useState<"connected" | "checking" | "disconnected">("checking");
  const [detail, setDetail] = useState("Checking backend sync");

  const check = async () => {
    if (!navigator.onLine) {
      setStatus("disconnected");
      setDetail("Browser offline");
      return;
    }
    try {
      setStatus("checking");
      const res = await api.health();
      setStatus(res.status === "ok" ? "connected" : "disconnected");
      setDetail(res.status === "ok" ? "Backend synced" : `Backend ${res.status}`);
    } catch (error) {
      console.error("[Connection] Health check failed", error);
      setStatus("disconnected");
      setDetail("Sync failed");
    }
  };

  useEffect(() => {
    check();
    const interval = setInterval(check, 30000);
    window.addEventListener("online", check);
    window.addEventListener("offline", check);
    return () => {
      clearInterval(interval);
      window.removeEventListener("online", check);
      window.removeEventListener("offline", check);
    };
  }, []);

  return (
    <div className="space-y-2">
      <div className={cn(
        "flex min-w-0 items-center gap-2 rounded-lg px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest transition-all",
        status === "connected" ? "text-emerald-400" : status === "disconnected" ? "text-rose-400" : "text-amber-400"
      )}>
        <div className={cn(
          "h-1.5 w-1.5 rounded-full",
          status === "connected" ? "bg-emerald-400 shadow-glow-emerald" : status === "disconnected" ? "bg-rose-400" : "bg-amber-400 animate-pulse"
        )} />
        <span className="flex-shrink-0">{status === "connected" ? "Online" : status === "disconnected" ? "Offline" : "Syncing"}</span>
        <span className="truncate text-neutral-600 normal-case tracking-normal">{detail}</span>
      </div>
      {status === "disconnected" && (
        <button onClick={check} className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest text-neutral-300 hover:bg-white/[0.06]">
          Retry connection
        </button>
      )}
    </div>
  );
}

export function Shell({ 
  active, 
  onNavigate, 
  children,
  products = []
}: { 
  active: string; 
  onNavigate: (page: string) => void; 
  children: ReactNode;
  products?: any[];
}) {
  const [collapsed, setCollapsed] = useState(false);
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-[#06060f] text-neutral-100 flex overflow-hidden">
      <AmbientBackground />
      
      {/* Floating Glass Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 80 : 270 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="relative z-50 hidden flex-shrink-0 flex-col glass-sidebar lg:flex"
      >
        {/* Logo */}
        <div className="flex min-w-0 items-center gap-3 border-b border-white/[0.04] px-5 py-6">
          <motion.div 
            whileHover={{ scale: 1.05, rotate: 5 }}
            className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 shadow-glow-lg text-white"
          >
            <BarChart3 className="h-5 w-5" />
          </motion.div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }} 
                animate={{ opacity: 1, x: 0 }} 
                exit={{ opacity: 0, x: -10 }}
                className="min-w-0 overflow-hidden whitespace-nowrap"
              >
                <div className="truncate text-sm font-extrabold tracking-wide text-white">Price Intel</div>
                <div className="truncate text-[9px] uppercase tracking-[0.2em] text-indigo-300/60 font-bold">AI Operations</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Collapse Toggle */}
        <motion.button
          whileHover={{ scale: 1.15 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3.5 top-9 flex h-7 w-7 items-center justify-center rounded-full glass border border-white/10 text-neutral-400 hover:text-white hover:border-indigo-500/30 transition-all z-50 shadow-glass"
        >
          {collapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
        </motion.button>

        {/* Command Menu */}
        <div className="px-3 py-3 border-b border-white/[0.04]">
          <CommandMenu setActive={onNavigate} products={products} />
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-0.5 custom-scrollbar">
          {nav.map(([label, Icon]) => {
            const isActive = active === label;
            const isHovered = hoveredItem === label;
            return (
              <motion.button
                key={label}
                onClick={() => onNavigate(label)}
                onMouseEnter={() => setHoveredItem(label)}
                onMouseLeave={() => setHoveredItem(null)}
                whileTap={{ scale: 0.97 }}
                className={cn(
                  "relative flex min-w-0 w-full items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition-all duration-200 group",
                  isActive ? "text-white" : "text-neutral-500 hover:text-neutral-200"
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active-indicator"
                    className="absolute inset-0 rounded-2xl overflow-hidden"
                    initial={false}
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  >
                    <div className="absolute inset-0 bg-white/[0.06] border border-white/[0.08]" style={{ borderRadius: 'inherit' }} />
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-indigo-500 rounded-r-full shadow-glow" />
                  </motion.div>
                )}
                
                {!isActive && isHovered && (
                  <motion.div
                    layoutId="sidebar-hover-indicator"
                    className="absolute inset-0 rounded-2xl bg-white/[0.03]"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                  />
                )}

                <motion.div
                  animate={isActive ? { scale: 1.1 } : isHovered ? { scale: 1.15, rotate: 5 } : { scale: 1, rotate: 0 }}
                  transition={{ type: "spring", stiffness: 400, damping: 20 }}
                >
                  <Icon className={cn(
                    "relative z-10 flex-shrink-0 h-[18px] w-[18px] transition-colors duration-200",
                    isActive ? "text-indigo-400" : "text-neutral-500 group-hover:text-neutral-300"
                  )} />
                </motion.div>
                
                <AnimatePresence>
                  {!collapsed && (
                    <motion.span 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="relative z-10 min-w-0 truncate whitespace-nowrap text-[13px]"
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.button>
            );
          })}
        </nav>
        
        {/* Connection Status */}
        <div className="px-3 py-2 border-t border-white/[0.04]">
          <ConnectionStatus />
        </div>

        {/* User Profile Footer */}
        <div className="p-4 border-t border-white/[0.04]">
          <div className={cn("flex items-center gap-3", collapsed ? "justify-center" : "justify-between")}>
             <div className="flex items-center gap-3 overflow-hidden">
                <motion.div 
                  whileHover={{ scale: 1.1 }}
                  className="h-9 w-9 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex-shrink-0 border border-white/20 flex items-center justify-center text-[11px] font-black text-white shadow-glow"
                >
                    {user?.name?.[0] || "U"}
                </motion.div>
                <AnimatePresence>
                  {!collapsed && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="text-[12px] font-bold text-white truncate">{user?.name || "Guest"}</div>
                      <div className="text-[9px] text-indigo-400/60 uppercase tracking-[0.2em] font-black">Pro Plan</div>
                    </motion.div>
                  )}
                </AnimatePresence>
             </div>
             <AnimatePresence>
               {!collapsed && (
                 <motion.button 
                   initial={{ opacity: 0 }}
                   animate={{ opacity: 1 }}
                   exit={{ opacity: 0 }}
                   whileHover={{ scale: 1.1 }}
                   whileTap={{ scale: 0.9 }}
                   onClick={logout}
                   className="p-2 rounded-xl bg-white/[0.03] border border-white/5 text-neutral-500 hover:text-rose-400 hover:bg-rose-400/10 hover:border-rose-400/20 transition-all"
                 >
                   <LogOut className="h-3.5 w-3.5" />
                 </motion.button>
               )}
             </AnimatePresence>
          </div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="relative min-w-0 flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar">
        <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={active}
              initial={{ opacity: 0, y: 12, filter: "blur(6px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -8, filter: "blur(6px)" }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
