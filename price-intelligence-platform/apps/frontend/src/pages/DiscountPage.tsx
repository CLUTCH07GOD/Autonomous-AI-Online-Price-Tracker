import { ShieldAlert, AlertTriangle, CheckCircle, Search, Zap } from "lucide-react";
import { DiscountAnalysis, Product } from "../types";
import { motion } from "framer-motion";

export function DiscountPage({ products, rows, scanningId, onScan }: { products: Product[]; rows: DiscountAnalysis[]; scanningId?: number; onScan: (id: number) => void }) {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
          <ShieldAlert className="h-8 w-8 text-rose-400" />
          Fake Discount Detector
        </h1>
        <p className="mt-2 text-sm text-neutral-400">Detect inflated MRP and manipulated discount claims using historical SQL prices.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {products.map((product) => (
          <motion.div 
            whileHover={{ y: -2 }}
            key={product.id} 
            className="glass-card-hover p-6"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <div className="text-sm font-bold text-white line-clamp-1">{product.title}</div>
                <div className="mt-2 flex items-center gap-3 text-xs text-neutral-500 font-medium">
                  <span className="flex items-center gap-1.5 rounded-lg bg-black px-2 py-1">
                    MRP: ₹{Number(product.mrp || 0).toLocaleString('en-IN')}
                  </span>
                  <span className="flex items-center gap-1.5 rounded-lg bg-black px-2 py-1 text-indigo-400">
                    Price: ₹{Number(product.current_best_price || 0).toLocaleString('en-IN')}
                  </span>
                </div>
              </div>
              <button 
                disabled={scanningId === product.id}
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white transition-all hover:bg-indigo-500 shadow-glow disabled:opacity-50" 
                onClick={() => onScan(product.id)}
              >
                {scanningId === product.id ? <Zap className="h-5 w-5 animate-pulse" /> : <Search className="h-5 w-5" />}
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="glass-card p-6">
        <div className="mb-6 flex items-center gap-2 font-bold text-white text-lg">
           <ShieldAlert className="h-5 w-5 text-rose-400" />
           Analysis Integrity History
        </div>
        <div className="space-y-4">
          {rows.map((row, index) => (
            <div className={`rounded-2xl border p-5 transition-all ${row.is_fake_discount ? 'bg-rose-500/5 border-rose-500/20' : 'bg-emerald-500/5 border-emerald-500/20'}`} key={`${row.product_id}-${index}`}>
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${row.is_fake_discount ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                    {row.is_fake_discount ? <AlertTriangle className="h-5 w-5" /> : <CheckCircle className="h-5 w-5" />}
                  </div>
                  <div>
                    <div className="text-sm font-bold text-white">Product #{row.product_id}</div>
                    <div className={`text-xs font-bold uppercase tracking-widest mt-0.5 ${row.is_fake_discount ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {row.is_fake_discount ? "Manipulated Discount Detected" : "Integrity Verified"}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                   <div className="text-[10px] text-neutral-500 font-bold uppercase tracking-wider mb-1">Confidence Score</div>
                   <div className="text-sm font-black text-white">{(Number(row.confidence) * 100).toFixed(0)}%</div>
                </div>
              </div>
              
              <div className="mt-4 grid grid-cols-2 gap-4">
                 <div className="rounded-xl bg-black/40 p-3 border border-white/5">
                    <div className="text-[10px] text-neutral-500 font-bold uppercase mb-1">Advertised Drop</div>
                    <div className="text-sm font-bold text-white">{row.advertised_discount_pct}%</div>
                 </div>
                 <div className="rounded-xl bg-black/40 p-3 border border-white/5">
                    <div className="text-[10px] text-neutral-500 font-bold uppercase mb-1">Real SQL Drop</div>
                    <div className={`text-sm font-bold ${Number(row.real_discount_pct) < Number(row.advertised_discount_pct) ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {row.real_discount_pct}%
                    </div>
                 </div>
              </div>
            </div>
          ))}
          {rows.length === 0 && (
            <div className="py-12 text-center text-sm text-neutral-500 border border-dashed border-white/[0.06] rounded-2xl">
               Run a scan to verify discount integrity.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

