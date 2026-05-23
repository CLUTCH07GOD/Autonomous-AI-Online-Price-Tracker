import { HeatmapCell } from "../types";
import { motion } from "framer-motion";
import { Map, Calendar, Tag } from "lucide-react";

export function HeatmapPage({ cells }: { cells: HeatmapCell[] }) {
  const max = Math.max(...cells.map((cell) => cell.avg_price), 1);
  
  // Group cells by category for a better layout
  const categories = Array.from(new Set(cells.map(c => c.category)));

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <Map className="h-8 w-8 text-indigo-400" />
            Price Heatmaps
          </h1>
          <p className="mt-2 text-sm text-neutral-400">Category/date heatmap generated from SQL price history aggregation.</p>
        </div>
      </div>

      <div className="glass-card p-8">
        <div className="mb-8 flex flex-wrap gap-6 items-center text-xs font-bold uppercase tracking-widest text-neutral-500">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Temporal Volatility
          </div>
          <div className="flex items-center gap-2">
            <Tag className="h-4 w-4" />
            Price Intensity
          </div>
          <div className="flex-1" />
          <div className="flex items-center gap-3">
             <span>Low</span>
             <div className="flex gap-1">
               {[0, 1, 2, 3, 4].map(i => (
                 <div key={i} className="h-3 w-6 rounded-sm" style={{ backgroundColor: `hsl(245 58% ${85 - i * 15}%)` }} />
               ))}
             </div>
             <span>High</span>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {cells.map((cell, index) => {
             const intensity = cell.avg_price / max;
             return (
               <motion.div 
                 key={`${cell.category}-${cell.date}-${index}`}
                 initial={{ opacity: 0, scale: 0.95 }}
                 animate={{ opacity: 1, scale: 1 }}
                 transition={{ delay: index * 0.02 }}
                 className="group relative rounded-2xl border border-white/5 p-4 transition-all hover:border-white/20 hover:shadow-[0_0_20px_rgba(79,70,229,0.15)] overflow-hidden"
                 style={{ 
                   backgroundColor: `hsl(245 58% ${92 - intensity * 40}%)` 
                 }}
               >
                 <div className="relative z-10">
                   <div className="text-xs font-bold uppercase tracking-tight text-indigo-900/60">{cell.category}</div>
                   <div className="text-[10px] text-indigo-800/50 font-medium mt-0.5">{cell.date}</div>
                   <div className="mt-3 text-xl font-black text-indigo-950 tracking-tighter">
                     ₹ {cell.avg_price.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                   </div>
                 </div>
                 
                 {/* Shine effect on hover */}
                 <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 pointer-events-none" />
               </motion.div>
             )
          })}
        </div>
        
        {cells.length === 0 && (
          <div className="py-20 text-center flex flex-col items-center justify-center border border-dashed border-neutral-800 rounded-2xl text-neutral-500">
             <Map className="h-10 w-10 mb-4 opacity-20" />
             <p>No heatmap data available yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}

