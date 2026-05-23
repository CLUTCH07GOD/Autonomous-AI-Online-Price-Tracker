import React from "react";
import { motion, useMotionTemplate, useMotionValue } from "framer-motion";
import { 
  TrendingDown, 
  TrendingUp, 
  DollarSign, 
  Package, 
  Activity, 
  Brain, 
  ArrowRight, 
  BarChart3, 
  Zap, 
  Bell, 
  Clock,
  ArrowUpRight,
  RefreshCw,
  Sparkles,
  Shield,
  Target
} from "lucide-react";
import { BentoGrid, BentoGridItem } from "../components/ui/BentoGrid";
import { DashboardMetrics, Product, ProductHistory } from "../types";
import { cn } from "../lib/utils";

interface DashboardProps {
  metrics?: DashboardMetrics;
  products: Product[];
  history?: ProductHistory;
  onRefresh: (id: number) => void;
}

function GlassStatCard({ label, value, icon: Icon, color, bg, delay = 0 }: {
  label: string; value: string | number; icon: any; color: string; bg: string; delay?: number;
}) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      onMouseMove={handleMouseMove}
      className="group relative overflow-hidden rounded-3xl glass-card-hover p-6 cursor-default"
    >
      {/* Spotlight follow effect */}
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              300px circle at ${mouseX}px ${mouseY}px,
              rgba(99, 102, 241, 0.06),
              transparent 80%
            )
          `,
        }}
      />

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={cn("p-2.5 rounded-2xl", bg)}>
            <Icon className={cn("h-5 w-5", color)} />
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-600">Live</span>
          </div>
        </div>
        <div className="text-3xl font-black text-white tracking-tight">{value}</div>
        <div className="text-sm text-neutral-500 mt-1.5 font-medium">{label}</div>
      </div>
    </motion.div>
  );
}

export function Dashboard({ metrics, products, onRefresh }: DashboardProps) {
  const recentProducts = products.slice(0, 4);
  const significantDrops = products
    .filter(p => p.current_best_price && p.mrp && p.current_best_price < p.mrp)
    .sort((a, b) => {
        const discA = a.mrp ? (a.mrp - (a.current_best_price || 0)) / a.mrp : 0;
        const discB = b.mrp ? (b.mrp - (b.current_best_price || 0)) / b.mrp : 0;
        return discB - discA;
    })
    .slice(0, 3);

  return (
    <div className="space-y-8 pb-12">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <motion.h2 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-3xl font-black tracking-tight text-white"
          >
            Intelligence Overview
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="text-neutral-500 mt-1.5 flex items-center gap-2"
          >
            <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
            Real-time market analytics and AI-driven price tracking
          </motion.p>
        </div>
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex gap-2"
        >
            <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06] text-sm font-medium text-neutral-400 hover:text-white hover:bg-white/[0.06] hover:border-white/[0.1] transition-all">
                <Clock className="h-4 w-4" />
                History
            </button>
            <button className="glass-button flex items-center gap-2 text-sm">
                <Zap className="h-4 w-4" />
                Smart Scan
            </button>
        </motion.div>
      </div>

      {/* Primary Stats - Glass Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassStatCard label="Total Tracked" value={metrics?.total_products || 0} icon={Package} color="text-blue-400" bg="bg-blue-400/10" delay={0} />
        <GlassStatCard label="Active Alerts" value={metrics?.active_alerts || 0} icon={Bell} color="text-purple-400" bg="bg-purple-400/10" delay={0.05} />
        <GlassStatCard label="Price Drops (24h)" value={metrics?.price_drops_24h || 0} icon={TrendingDown} color="text-emerald-400" bg="bg-emerald-400/10" delay={0.1} />
        <GlassStatCard label="Total Savings" value={`₹${(metrics?.total_savings || 0).toLocaleString()}`} icon={DollarSign} color="text-amber-400" bg="bg-amber-400/10" delay={0.15} />
      </div>

      {/* Main Bento Grid */}
      <BentoGrid className="md:auto-rows-[20rem]">
        {/* Large Feature: Top Price Drops */}
        <BentoGridItem
          className="md:col-span-2 md:row-span-2"
          title="Top Discount Opportunities"
          description="AI-detected price drops with high confidence scores."
          header={
            <div className="flex-1 w-full h-full min-h-[10rem] rounded-2xl p-4 overflow-hidden relative bg-gradient-to-br from-neutral-800/50 to-neutral-950/50 backdrop-blur-sm border border-white/[0.04]">
                <div className="absolute top-0 right-0 p-4 opacity-[0.04]">
                    <TrendingDown className="h-32 w-32" />
                </div>
                <div className="space-y-3 relative z-10">
                    {significantDrops.length > 0 ? significantDrops.map((product, idx) => (
                        <motion.div 
                          key={product.id} 
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="flex items-center gap-4 p-3 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-indigo-500/30 hover:bg-white/[0.04] transition-all group cursor-pointer"
                        >
                            <div className="h-12 w-12 rounded-xl bg-white/90 overflow-hidden flex-shrink-0 shadow-lg">
                                <img src={product.image_url || ""} className="h-full w-full object-contain p-1" alt="" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="text-sm font-bold text-white truncate">{product.title}</div>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="text-emerald-400 font-bold">₹{product.current_best_price?.toLocaleString()}</span>
                                    <span className="text-xs text-neutral-600 line-through">₹{product.mrp?.toLocaleString()}</span>
                                    <span className="text-[10px] bg-emerald-500/15 text-emerald-400 px-2 py-0.5 rounded-full font-bold border border-emerald-500/20">
                                        -{Math.round((product.mrp! - product.current_best_price!) / product.mrp! * 100)}%
                                    </span>
                                </div>
                            </div>
                            <ArrowUpRight className="h-4 w-4 text-neutral-600 group-hover:text-indigo-400 transition-colors" />
                        </motion.div>
                    )) : (
                        <div className="h-full flex flex-col items-center justify-center text-neutral-600 py-12">
                            <Package className="h-8 w-8 mb-2 opacity-20" />
                            <p className="text-sm">Track products to see discount opportunities</p>
                        </div>
                    )}
                </div>
            </div>
          }
          icon={<Zap className="h-4 w-4 text-amber-400" />}
        />

        {/* Medium Feature: AI Confidence */}
        <BentoGridItem
          className="md:col-span-1 md:row-span-1"
          title="AI Confidence"
          description="Model accuracy across retailers."
          header={
            <div className="flex-1 flex flex-col items-center justify-center space-y-4 py-4">
                <div className="relative h-24 w-24">
                    <svg className="h-full w-full -rotate-90" viewBox="0 0 36 36">
                        <path className="text-white/[0.04]" stroke="currentColor" strokeWidth="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        <motion.path 
                          initial={{ strokeDasharray: "0, 100" }}
                          animate={{ strokeDasharray: "92, 100" }}
                          transition={{ duration: 1.5, ease: "easeOut" }}
                          className="text-indigo-500" 
                          stroke="currentColor" strokeWidth="3" strokeLinecap="round" fill="none" 
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                          style={{ filter: "drop-shadow(0 0 6px rgba(99,102,241,0.5))" }}
                        />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center text-xl font-black text-white">92%</div>
                </div>
                <div className="text-[9px] font-black uppercase tracking-[0.2em] text-neutral-600 flex items-center gap-1.5">
                  <Brain className="h-3 w-3 text-purple-400" />
                  ML Optimizing
                </div>
            </div>
          }
          icon={<Brain className="h-4 w-4 text-purple-400" />}
        />

        {/* Small Feature: Retailer Health */}
        <BentoGridItem
          className="md:col-span-1 md:row-span-1"
          title="Retailer Health"
          description="Scraper connection status."
          header={
            <div className="flex-1 flex flex-col gap-2 py-2">
                {["Amazon", "Flipkart", "Myntra", "Ajio", "Reliance"].map((site, i) => (
                    <motion.div 
                      key={site} 
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-white/[0.08] transition-all"
                    >
                        <span className="text-xs font-medium text-neutral-400">{site}</span>
                        <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
                    </motion.div>
                ))}
            </div>
          }
          icon={<Activity className="h-4 w-4 text-emerald-400" />}
        />

        {/* Large Feature: Market Movement */}
        <BentoGridItem
          className="md:col-span-3 md:row-span-1"
          title="Real-time Market Movement"
          description="Tracking price fluctuations across 5 major retailers."
          header={
            <div className="flex-1 w-full flex items-end justify-around gap-3 px-4 pb-4">
               {[
                 { day: "Mon", val: 40 }, { day: "Tue", val: 70 }, { day: "Wed", val: 50 },
                 { day: "Thu", val: 90 }, { day: "Fri", val: 60 }, { day: "Sat", val: 80 }, { day: "Sun", val: 95 }
               ].map((d, i) => (
                 <div key={d.day} className="flex flex-col items-center gap-2 flex-1">
                    <div className="w-full h-[100px] bg-white/[0.02] rounded-xl relative overflow-hidden border border-white/[0.03]">
                        <motion.div 
                            initial={{ height: 0 }}
                            animate={{ height: `${d.val}%` }}
                            transition={{ delay: 0.3 + i * 0.08, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                            className="absolute bottom-0 left-0 right-0 rounded-xl"
                            style={{ 
                              background: `linear-gradient(to top, rgba(99,102,241,0.7), rgba(99,102,241,0.3))`,
                              boxShadow: "0 0 15px rgba(99,102,241,0.2)"
                            }}
                        />
                    </div>
                    <span className="text-[10px] font-bold text-neutral-600 uppercase">{d.day}</span>
                 </div>
               ))}
            </div>
          }
          icon={<BarChart3 className="h-4 w-4 text-indigo-400" />}
        />
      </BentoGrid>

      {/* Recent Activity Section */}
      <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Clock className="h-5 w-5 text-neutral-600" />
                Recent Product Activity
            </h3>
            <button className="text-sm font-bold text-indigo-400/70 hover:text-indigo-300 transition-colors flex items-center gap-1">
                View All
                <ArrowRight className="h-4 w-4" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recentProducts.map((product, idx) => (
                  <motion.div 
                    key={product.id} 
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 + idx * 0.05 }}
                    className="flex items-center gap-4 p-4 glass-card-hover group cursor-default"
                  >
                      <div className="h-14 w-14 rounded-2xl bg-white/90 p-2 flex-shrink-0 shadow-lg">
                          <img src={product.image_url || ""} className="h-full w-full object-contain" alt="" />
                      </div>
                      <div className="flex-1 min-w-0">
                          <div className="text-sm font-bold text-white truncate">{product.title}</div>
                          <div className="text-[10px] text-neutral-600 mt-0.5 uppercase tracking-wider font-bold">{product.category}</div>
                          <div className="flex items-center gap-2 mt-2">
                             <div className="text-lg font-black text-white">₹{(product.current_best_price || 0).toLocaleString()}</div>
                             <motion.button 
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                onClick={() => onRefresh(product.id)}
                                className="p-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:bg-indigo-500/10 hover:border-indigo-500/20 text-neutral-500 hover:text-indigo-400 transition-all"
                             >
                                <RefreshCw className="h-3 w-3" />
                             </motion.button>
                          </div>
                      </div>
                      <div className="text-right">
                          <div className={cn(
                              "text-[10px] font-bold px-2.5 py-1 rounded-lg inline-block border",
                              product.availability === "In Stock" 
                                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
                                : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                          )}>
                              {product.availability}
                          </div>
                      </div>
                  </motion.div>
              ))}
          </div>
      </div>
    </div>
  );
}
