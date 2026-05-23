import { Recommendation } from "../types";
import { Sparkles, RefreshCcw, ShieldCheck, Zap } from "lucide-react";
import { motion } from "framer-motion";

export function RecommendationPage({ rows, onRefresh }: { rows: Recommendation[]; onRefresh: () => void }) {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <Sparkles className="h-8 w-8 text-yellow-400" />
            Recommendation Center
          </h1>
          <p className="mt-2 text-sm text-neutral-400">Personalized buy/wait decisions with explainable AI scores.</p>
        </div>
        <button 
          className="inline-flex items-center gap-2 rounded-xl bg-white/[0.03] border border-white/[0.06] px-5 py-2.5 text-sm font-semibold text-white transition-all hover:bg-white/[0.06] hover:border-white/[0.1]" 
          onClick={onRefresh}
        >
          <RefreshCcw className="h-4 w-4" />
          Regenerate AI
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {rows.length === 0 ? (
          <div className="col-span-full flex h-40 items-center justify-center rounded-2xl border border-dashed border-white/[0.06] text-neutral-500">
            No recommendations generated. Refresh to run the AI engine.
          </div>
        ) : rows.map((row, idx) => {
          const isBuy = row.type === "BUY NOW";
          const scorePercent = Math.min(row.score * 100, 100);
          return (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="group relative overflow-hidden glass-card-hover p-6" 
              key={`${row.product_id}-${row.type}`}
            >
              {isBuy && <div className="absolute top-0 right-0 p-24 bg-emerald-500/10 blur-[60px] rounded-full pointer-events-none" />}
              
              <div className="relative z-10 flex items-start justify-between gap-4">
                <div className="font-semibold text-white text-lg leading-tight">{row.title}</div>
                <div className={`flex-shrink-0 rounded-lg px-3 py-1.5 text-xs font-bold border flex items-center gap-1.5 ${
                  isBuy 
                  ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' 
                  : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                }`}>
                  {isBuy ? <Zap className="h-3 w-3" /> : <ShieldCheck className="h-3 w-3" />}
                  {row.type}
                </div>
              </div>
              
              <div className="relative z-10 mt-4 text-sm text-neutral-400 bg-black/40 rounded-xl p-4 border border-white/5">
                {row.content}
              </div>
              
              <div className="relative z-10 mt-6">
                <div className="flex justify-between text-xs mb-2">
                  <span className="text-neutral-500">Confidence Score</span>
                  <span className={isBuy ? "text-emerald-400 font-bold" : "text-amber-400 font-bold"}>{Math.round(scorePercent)}%</span>
                </div>
                <div className="h-2.5 rounded-full bg-neutral-800 overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${scorePercent}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className={`h-full rounded-full ${
                      isBuy 
                      ? 'bg-gradient-to-r from-emerald-600 to-emerald-400' 
                      : 'bg-gradient-to-r from-amber-600 to-amber-400'
                    }`} 
                  />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
