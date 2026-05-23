import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Search, 
  Trash2, 
  ExternalLink, 
  TrendingDown, 
  TrendingUp, 
  Minus, 
  Package, 
  Plus, 
  Loader2, 
  CheckCircle2, 
  AlertCircle,
  ShieldCheck,
  ShoppingBag,
  Globe
} from "lucide-react";
import { Product } from "../types";
import { cn } from "../lib/utils";

interface ProductSearchProps {
  url: string;
  setUrl: (url: string) => void;
  loading: boolean;
  products: Product[];
  onTrack: () => void;
  onDelete: (id: number) => void;
  action: string;
}

export function ProductSearch({ url, setUrl, loading, products, onTrack, onDelete }: ProductSearchProps) {
  const [platform, setPlatform] = useState<string | null>(null);
  const [stage, setStage] = useState(0);
  
  const stages = [
    "Initializing crawler...",
    "Bypassing anti-bot systems...",
    "Extracting DOM elements...",
    "Parsing price data...",
    "Finalizing tracking..."
  ];

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setStage((prev) => (prev + 1) % stages.length);
      }, 1500);
      return () => clearInterval(interval);
    } else {
      setStage(0);
    }
  }, [loading]);

  useEffect(() => {
    if (url.includes("amazon")) setPlatform("amazon");
    else if (url.includes("flipkart")) setPlatform("flipkart");
    else if (url.includes("myntra")) setPlatform("myntra");
    else if (url.includes("ajio")) setPlatform("ajio");
    else if (url.includes("reliance")) setPlatform("reliance");
    else setPlatform(null);
  }, [url]);

  return (
    <div className="space-y-8 pb-12">
      {/* Search Header */}
      <div className="relative group">
        <div className="absolute -inset-1 rounded-[2rem] bg-indigo-500/10 blur-xl opacity-40 transition duration-500 group-hover:opacity-60" />
        <div className="relative glass-card p-5 sm:p-7 lg:p-8 overflow-hidden">
          <h2 className="text-2xl font-bold text-white mb-2 leading-tight">Track New Product</h2>
          <p className="text-neutral-400 mb-6 max-w-3xl leading-relaxed">Paste an ecommerce URL to start monitoring prices with AI.</p>
          
          <div className="flex min-w-0 flex-col lg:flex-row gap-4">
            <div className="glass-input flex h-16 min-w-0 flex-1 items-center gap-3 rounded-2xl overflow-hidden px-4 py-0">
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-white/[0.04]">
                {platform ? (
                  <Globe className="h-4 w-4 text-indigo-400" />
                ) : (
                  <Search className="h-4 w-4 text-neutral-500" />
                )}
              </div>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste Amazon, Flipkart, Myntra, Ajio or Reliance URL..."
                className="min-w-0 flex-1 truncate bg-transparent py-4 text-base font-semibold text-white placeholder-neutral-500 outline-none"
              />
              {platform && (
                <div className="hidden flex-shrink-0 rounded-lg border border-indigo-500/30 bg-indigo-500/15 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-indigo-300 sm:block">
                  {platform} detected
                </div>
              )}
            </div>
            <button
              onClick={onTrack}
              disabled={loading || !url}
              className="glass-button flex h-16 flex-shrink-0 items-center justify-center gap-2 rounded-2xl px-6 sm:px-8 disabled:opacity-50 lg:min-w-[190px]"
            >
              {loading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <Plus className="h-5 w-5" />
                  <span className="whitespace-nowrap">Track Product</span>
                </>
              )}
            </button>
          </div>

          <AnimatePresence>
            {loading && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="mt-6 flex flex-col items-center gap-4 py-8 rounded-2xl bg-black/40 border border-white/5"
              >
                 <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full border-2 border-indigo-500/20 border-t-indigo-500 animate-spin" />
                    <div className="text-lg font-medium text-white">{stages[stage]}</div>
                 </div>
                 <div className="w-full max-w-md bg-white/5 h-1 rounded-full overflow-hidden">
                    <motion.div 
                        initial={{ width: "0%" }}
                        animate={{ width: `${(stage + 1) * 20}%` }}
                        className="h-full bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]"
                    />
                 </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Tracked Products List */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="min-w-0 text-xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 flex-shrink-0 text-emerald-400" />
            <span className="truncate">Currently Tracking</span>
          </h3>
          <span className="flex-shrink-0 text-xs font-bold text-neutral-500 uppercase tracking-widest bg-white/5 px-3 py-1 rounded-full">{products.length} Products</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AnimatePresence mode="popLayout">
            {products.map((product) => (
              <motion.div
                key={product.id}
                layout
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                className="group relative glass-card-hover p-6 overflow-hidden"
              >
                {/* Background glow on hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 via-transparent to-purple-600/0 group-hover:from-indigo-500/5 group-hover:to-purple-600/5 transition-all duration-500 pointer-events-none" />

                <div className="flex flex-col gap-5 relative z-10 sm:flex-row sm:gap-6">
                  <div className="relative h-28 w-28 flex-shrink-0 bg-white rounded-3xl p-3 shadow-lg group-hover:scale-105 transition-transform duration-300">
                    <img src={product.image_url || ""} alt="" className="h-full w-full object-contain" />
                    {product.mrp && product.current_best_price && product.current_best_price < product.mrp && (
                      <div className="absolute -top-2 -right-2 bg-emerald-500 text-white text-[10px] font-black px-2 py-1 rounded-lg shadow-lg uppercase tracking-tighter">
                         -{Math.round((product.mrp - product.current_best_price) / product.mrp * 100)}%
                      </div>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-1">
                        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 flex items-center gap-2">
                            <ShoppingBag className="h-3 w-3" />
                            {product.category || "General"}
                        </div>
                        <h4 className="text-lg font-bold text-white truncate group-hover:text-indigo-400 transition-colors">{product.title}</h4>
                      </div>
                      <div className="flex gap-1">
                        <a href={product.links?.[0]?.url} target="_blank" rel="noreferrer" className="p-2 rounded-xl bg-white/5 text-neutral-400 hover:text-white hover:bg-white/10 transition-all">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                        <button
                          onClick={() => onDelete(product.id)}
                          className="p-2 rounded-xl bg-white/5 text-neutral-500 hover:text-rose-400 hover:bg-rose-400/10 transition-all"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>

                    <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                      <div className="space-y-1">
                        <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Current Price</div>
                        <div className="flex min-w-0 flex-wrap items-baseline gap-3">
                            <div className="text-2xl font-black text-white">₹{(product.current_best_price || 0).toLocaleString()}</div>
                            {product.mrp && (
                                <div className="text-sm text-neutral-500 line-through font-medium">₹{product.mrp.toLocaleString()}</div>
                            )}
                        </div>
                      </div>
                      
                      <div className="flex flex-col items-end gap-2">
                         {(() => {
                           const status = product.links?.[0]?.scrape_status || 'SUCCESS';
                           const error = product.links?.[0]?.error_message;
                           
                           if (status === 'BLOCKED') {
                             return (
                               <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20" title={error || "Bot protection blocked scraper"}>
                                 <AlertCircle className="h-3 w-3" />
                                 BLOCKED
                               </div>
                             );
                           }
                           
                           if (status === 'FAILED') {
                             return (
                               <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20" title={error || "Scraping failed"}>
                                 <AlertCircle className="h-3 w-3" />
                                 FAILED
                               </div>
                             );
                           }

                           return (
                             <div className={cn(
                                "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all",
                                product.availability === "In Stock" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                             )}>
                                <div className={cn("h-1.5 w-1.5 rounded-full", product.availability === "In Stock" ? "bg-emerald-500" : "bg-rose-500")} />
                                {product.availability || "Unknown"}
                             </div>
                           );
                         })()}
                         <div className="flex items-center gap-1 text-[10px] font-bold text-neutral-500 uppercase tracking-tighter">
                            Next Prediction: <span className="text-indigo-400">Stable</span>
                         </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI Insight Footer */}
                <div className="mt-6 pt-4 border-t border-white/5 flex flex-col gap-3 text-xs sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex min-w-0 flex-wrap items-center gap-4">
                        <div className="flex items-center gap-1 text-neutral-400">
                            <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                            98% Confidence
                        </div>
                        <div className="flex items-center gap-1 text-neutral-400">
                            <TrendingDown className="h-3 w-3 text-emerald-400" />
                            Lowest in 30 days
                        </div>
                    </div>
                    <button className="text-indigo-400 font-bold hover:text-indigo-300 transition-colors uppercase tracking-widest text-[10px]">Analyze Details</button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {products.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 rounded-[3rem] border border-dashed border-white/[0.06] bg-white/[0.01]">
             <Package className="h-16 w-16 text-neutral-700 mb-4" />
             <h4 className="text-xl font-bold text-neutral-400">No products tracked yet</h4>
             <p className="text-neutral-500 text-sm mt-1">Add your first product URL above to start saving.</p>
          </div>
        )}
      </div>
    </div>
  );
}
