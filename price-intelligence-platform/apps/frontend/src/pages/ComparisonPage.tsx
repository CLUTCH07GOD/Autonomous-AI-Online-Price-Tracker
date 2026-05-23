import React from "react";
import { motion } from "framer-motion";
import { 
  ArrowLeftRight, 
  Search, 
  ChevronRight, 
  ExternalLink, 
  Star, 
  TrendingDown, 
  TrendingUp, 
  Zap, 
  ShieldCheck,
  Award,
  ArrowUpRight
} from "lucide-react";
import { cn } from "../lib/utils";
import { ComparisonResult } from "../types";

interface ComparisonPageProps {
  query: string;
  setQuery: (q: string) => void;
  rows: ComparisonResult[];
  onSearch: () => void;
}

export function ComparisonPage({ query, setQuery, rows, onSearch }: ComparisonPageProps) {
  return (
    <div className="space-y-8 pb-12">
      {/* Search Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-3xl font-bold text-white tracking-tight">Market Comparison</h2>
          <p className="text-neutral-400 mt-1">Cross-retailer price matrix and value analysis.</p>
        </div>
        <div className="flex gap-4 flex-1 max-w-xl">
          <div className="relative flex-1 group">
            <div className="absolute -inset-0.5 bg-indigo-500/20 rounded-2xl blur group-focus-within:opacity-100 opacity-0 transition duration-500"></div>
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSearch()}
              placeholder="Search across all retailers..."
              className="glass-input w-full px-12 py-4 rounded-2xl text-white relative z-10"
            />
          </div>
          <button
            onClick={onSearch}
            className="glass-button rounded-2xl px-8 whitespace-nowrap"
          >
            Run Matrix
          </button>
        </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 gap-8">
        {rows.length > 0 ? rows.map((row, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card-hover p-8"
          >
            <div className="flex flex-col lg:flex-row gap-8">
              {/* Product Info */}
              <div className="lg:w-1/3 space-y-6">
                <div className="relative group">
                    <div className="absolute -inset-4 bg-indigo-500/5 rounded-[2rem] blur-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <div className="h-64 w-full bg-white rounded-3xl p-8 shadow-2xl relative">
                        <img src={row.image_url || ""} alt="" className="h-full w-full object-contain" />
                    </div>
                </div>
                <div className="space-y-2">
                    <div className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Market Leader</div>
                    <h3 className="text-2xl font-bold text-white line-clamp-2">{row.title}</h3>
                    <div className="flex items-center gap-2">
                        <div className="flex gap-0.5">
                            {[1,2,3,4,5].map(s => <Star key={s} className="h-3 w-3 fill-amber-400 text-amber-400" />)}
                        </div>
                        <span className="text-xs font-bold text-neutral-500">4.8 (2,450 Reviews)</span>
                    </div>
                </div>
              </div>

              {/* Comparison Table */}
              <div className="flex-1 space-y-4">
                 <div className="grid grid-cols-4 text-[10px] font-black uppercase tracking-widest text-neutral-500 px-4">
                    <span>Retailer</span>
                    <span className="text-center">Availability</span>
                    <span className="text-center">Price</span>
                    <span className="text-right">Action</span>
                 </div>
                 
                 <div className="space-y-3">
                    {(row.retailers ?? []).map((ret, idx) => (
                        <div 
                            key={idx}
                            className={cn(
                                "grid grid-cols-4 items-center p-4 rounded-2xl border transition-all",
                                idx === 0 ? "bg-indigo-600/10 border-indigo-500/30" : "bg-black/20 border-white/5 hover:border-white/10"
                            )}
                        >
                            <div className="flex items-center gap-3">
                                <div className="h-8 w-8 rounded-lg bg-white p-1 flex-shrink-0">
                                    <img src={`https://www.google.com/s2/favicons?domain=${ret.domain}&sz=64`} alt="" className="h-full w-full object-contain" />
                                </div>
                                <span className="text-sm font-bold text-white">{ret.name}</span>
                            </div>
                            <div className="text-center">
                                <span className={cn(
                                    "text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-tighter",
                                    ret.in_stock ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                                )}>
                                    {ret.in_stock ? "In Stock" : "Out of Stock"}
                                </span>
                            </div>
                            <div className="text-center">
                                <div className="text-lg font-black text-white">₹{(ret.price ?? 0).toLocaleString()}</div>
                                {idx === 0 && <div className="text-[10px] text-emerald-400 font-bold uppercase">Lowest Price</div>}
                            </div>
                            <div className="text-right">
                                <a href={ret.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-xs font-bold text-white hover:bg-white/10 transition-all">
                                    Visit
                                    <ArrowUpRight className="h-3 w-3" />
                                </a>
                            </div>
                        </div>
                    ))}
                    {(row.retailers ?? []).length === 0 && (
                        <div className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-neutral-500">
                            No retailer offers are available for this product yet.
                        </div>
                    )}
                 </div>

                 {/* AI Analysis Overlay */}
                 <div className="mt-8 p-6 rounded-3xl bg-indigo-600/5 border border-indigo-500/10 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="h-12 w-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                            <Zap className="h-6 w-6" />
                        </div>
                        <div>
                            <div className="text-sm font-bold text-white">AI Recommendation</div>
                            <div className="text-xs text-neutral-400">Flipkart is currently offering the best value with a 15% lower price than market average.</div>
                        </div>
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-xs font-bold text-white hover:bg-indigo-500 transition-all">
                        Track Best Deal
                    </button>
                 </div>
              </div>
            </div>
          </motion.div>
        )) : (
            <div className="flex flex-col items-center justify-center py-40 rounded-[3rem] border border-dashed border-white/[0.06] bg-white/[0.01]">
                <ArrowLeftRight className="h-16 w-16 text-neutral-700 mb-4 opacity-20" />
                <h4 className="text-xl font-bold text-neutral-400">Ready to compare</h4>
                <p className="text-neutral-500 text-sm mt-1 max-w-md text-center">Search for any product to generate a real-time price matrix across all retailers.</p>
            </div>
        )}
      </div>
    </div>
  );
}
