import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bell, 
  BellRing, 
  Plus, 
  Trash2, 
  Mail, 
  Smartphone, 
  CheckCircle2, 
  AlertCircle,
  Clock,
  Target,
  Zap,
  TrendingDown,
  History
} from "lucide-react";
import { AlertRecord, NotificationRecord, Product } from "../types";
import { cn } from "../lib/utils";

interface AlertsPageProps {
  products: Product[];
  alerts: AlertRecord[];
  notifications: NotificationRecord[];
  target: string;
  setTarget: (t: string) => void;
  percentageDrop: string;
  setPercentageDrop: (p: string) => void;
  lowestDays: string;
  setLowestDays: (d: string) => void;
  selected: number | "";
  setSelected: (id: number | "") => void;
  onCreate: () => void;
  onToggle: (id: number) => void;
}

export function AlertsPage({ products, alerts, notifications, target, setTarget, percentageDrop, setPercentageDrop, lowestDays, setLowestDays, selected, setSelected, onCreate, onToggle }: AlertsPageProps) {
  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
             <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center shadow-glow">
                <Bell className="h-6 w-6 text-white" />
             </div>
             Smart Price Alerts
          </h2>
          <p className="text-neutral-400 mt-1">Get notified instantly when prices hit your target.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Create Alert Section */}
        <div className="lg:col-span-1">
          <div className="glass-card p-8 relative overflow-hidden group">
            <div className="absolute -inset-1 bg-gradient-to-br from-indigo-500/10 to-purple-600/10 blur opacity-50 pointer-events-none" />
            <h3 className="text-xl font-bold text-white mb-6 relative z-10">Configure Alert</h3>
            
            <div className="space-y-6 relative z-10">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-neutral-500 px-1">Select Product</label>
                <select 
                  value={selected}
                  onChange={(e) => setSelected(e.target.value ? Number(e.target.value) : "")}
                  className="glass-input w-full px-4 py-4 text-sm appearance-none cursor-pointer rounded-2xl"
                >
                  <option value="">Choose a product...</option>
                  {products.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-neutral-500 px-1">Target Price (INR)</label>
                <div className="relative">
                    <Target className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-500" />
                    <input
                        type="number"
                        value={target}
                        onChange={(e) => setTarget(e.target.value)}
                        placeholder="e.g. 14999"
                        className="glass-input w-full px-12 py-4 font-bold text-lg rounded-2xl"
                    />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-neutral-500 px-1">Percentage Drop (%)</label>
                <div className="relative">
                    <TrendingDown className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-emerald-500" />
                    <input
                        type="number"
                        value={percentageDrop}
                        onChange={(e) => setPercentageDrop(e.target.value)}
                        placeholder="e.g. 15 for 15% drop"
                        className="w-full rounded-2xl border border-white/10 bg-black/40 px-12 py-4 text-white placeholder-neutral-600 focus:border-indigo-500 outline-none transition-all font-bold text-lg"
                    />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-widest text-neutral-500 px-1">Lowest in X Days</label>
                <div className="relative">
                    <History className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-indigo-400" />
                    <input
                        type="number"
                        value={lowestDays}
                        onChange={(e) => setLowestDays(e.target.value)}
                        placeholder="e.g. 30"
                        className="w-full rounded-2xl border border-white/10 bg-black/40 px-12 py-4 text-white placeholder-neutral-600 focus:border-indigo-500 outline-none transition-all font-bold text-lg"
                    />
                </div>
              </div>

              <div className="space-y-4 pt-2">
                  <div className="flex items-center justify-between p-4 rounded-2xl bg-black/20 border border-white/5">
                      <div className="flex items-center gap-3">
                          <Mail className="h-5 w-5 text-indigo-400" />
                          <span className="text-sm font-medium text-neutral-300">Email Alerts</span>
                      </div>
                      <div className="h-6 w-11 rounded-full bg-indigo-600 p-1 flex justify-end cursor-pointer"><div className="h-4 w-4 rounded-full bg-white" /></div>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-2xl bg-black/20 border border-white/5">
                      <div className="flex items-center gap-3">
                          <Smartphone className="h-5 w-5 text-purple-400" />
                          <span className="text-sm font-medium text-neutral-300">Push Notifications</span>
                      </div>
                      <div className="h-6 w-11 rounded-full bg-neutral-800 p-1 flex justify-start cursor-pointer"><div className="h-4 w-4 rounded-full bg-neutral-600" /></div>
                  </div>
              </div>

              <button
                onClick={onCreate}
                disabled={!selected || !target}
                className="glass-button w-full py-4 rounded-2xl flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Plus className="h-5 w-5" />
                Activate Smart Alert
              </button>
            </div>
          </div>
        </div>

        {/* Alerts List */}
        <div className="lg:col-span-2 space-y-6">
           <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-white">Active Monitors</h3>
              <div className="text-[10px] font-black uppercase tracking-widest text-neutral-500">{alerts.length} Monitors Active</div>
           </div>

           <div className="grid grid-cols-1 gap-4">
              <AnimatePresence mode="popLayout">
                {alerts.map((alert) => {
                  const product = products.find(p => p.id === alert.product_id);
                  return (
                    <motion.div
                      key={alert.id}
                      layout
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="glass-card-hover p-6 flex items-center gap-6 group"
                    >
                        <div className="h-16 w-16 rounded-2xl bg-white p-2 flex-shrink-0 relative overflow-hidden">
                           <img src={product?.image_url || ""} alt="" className="h-full w-full object-contain" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                           <h4 className="text-sm font-bold text-white truncate">{product?.title || "Unknown Product"}</h4>
                           <div className="flex items-center gap-4 mt-2">
                               <div>
                                  <div className="text-[10px] text-neutral-500 font-bold uppercase">Current</div>
                                  <div className="text-sm font-bold text-white">₹{product?.current_best_price?.toLocaleString() || "---"}</div>
                               </div>
                               <div className="h-6 w-px bg-white/5" />
                               <div>
                                  <div className="text-[10px] text-indigo-400 font-bold uppercase tracking-tighter">Target</div>
                                  <div className="text-sm font-bold text-indigo-400">₹{alert.target_price.toLocaleString()}</div>
                                </div>
                           </div>
                        </div>

                        <div className="flex flex-col items-end gap-3">
                           <div 
                              onClick={() => onToggle(alert.id)}
                              className={cn(
                                "flex items-center gap-2 px-3 py-1.5 rounded-xl cursor-pointer transition-all",
                                alert.is_active ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-neutral-800 text-neutral-500 border border-white/5"
                              )}
                           >
                              <div className={cn("h-1.5 w-1.5 rounded-full animate-pulse", alert.is_active ? "bg-emerald-500" : "bg-neutral-600")} />
                              <span className="text-[10px] font-black uppercase tracking-widest">{alert.is_active ? "Active" : "Paused"}</span>
                           </div>
                           <button className="text-neutral-500 hover:text-rose-400 transition-colors">
                              <Trash2 className="h-4 w-4" />
                           </button>
                        </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
              
              {alerts.length === 0 && (
                <div className="py-20 rounded-[2.5rem] border border-dashed border-white/[0.06] bg-white/[0.01] flex flex-col items-center justify-center text-neutral-500">
                    <BellRing className="h-12 w-12 mb-4 opacity-10" />
                    <p className="text-sm font-medium">No alerts configured</p>
                </div>
              )}
           </div>

           {/* Notification History */}
           <div className="pt-8">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Clock className="h-5 w-5 text-neutral-500" />
                  Trigger History
              </h3>
              <div className="space-y-3">
                  {notifications.slice(0, 5).map((n, i) => (
                    <div key={i} className="flex items-center gap-4 p-4 rounded-2xl bg-black/20 border border-white/5">
                        <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                            <Zap className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                            <div className="text-xs font-bold text-white">{n.title}</div>
                            <div className="text-[10px] text-neutral-500 mt-0.5">{n.content}</div>
                        </div>
                        <div className="text-[10px] font-bold text-neutral-600 uppercase whitespace-nowrap">
                            {n.created_at ? new Date(n.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : "Just now"}
                        </div>
                    </div>
                  ))}
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
