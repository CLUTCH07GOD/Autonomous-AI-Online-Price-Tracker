import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ProductHistory } from "../types";
import { History, TrendingDown, TrendingUp, Activity, Target } from "lucide-react";
import { motion } from "framer-motion";

export function HistoricalAnalytics({ data, onSelect }: { data?: ProductHistory; onSelect: (id: number) => void }) {
  const chart = data?.history.map((item) => ({ ...item, date: new Date(item.captured_at).toLocaleDateString() })) || [];
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            <History className="h-8 w-8 text-indigo-400" />
            Historical Intelligence
          </h1>
          <p className="mt-2 text-sm text-neutral-400">SQL-backed price history, min/max/average price, and volatility scoring.</p>
        </div>
      </div>

      <div className="glass-card p-6">
        <div className="flex flex-col md:flex-row gap-6 items-center">
          <div className="w-full md:w-1/3">
             <label className="block space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-neutral-500 px-1">Selected Product</span>
                <select 
                  className="w-full rounded-xl border border-white/10 bg-black px-4 py-3 text-sm text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all cursor-pointer shadow-lg" 
                  value={data?.selected_product_id || ""} 
                  onChange={(event) => onSelect(Number(event.target.value))}
                >
                  {data?.products.map((product) => <option key={product.id} value={product.id}>{product.title}</option>)}
                </select>
             </label>
          </div>
          <div className="grid flex-1 grid-cols-2 lg:grid-cols-4 gap-4 w-full">
            <Stat label="Lowest" value={data?.stats.lowest ?? 0} icon={TrendingDown} color="text-emerald-400" />
            <Stat label="Highest" value={data?.stats.highest ?? 0} icon={TrendingUp} color="text-rose-400" />
            <Stat label="Average" value={data?.stats.average ?? 0} icon={Target} color="text-indigo-400" />
            <Stat label="Volatility" value={data?.volatility ?? 0} icon={Activity} color="text-amber-400" />
          </div>
        </div>
      </div>

      <div className="glass-card p-8 relative overflow-hidden h-[450px]">
        <div className="absolute top-0 right-0 p-32 bg-indigo-500/5 blur-[100px] rounded-full pointer-events-none" />
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chart} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="historyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#818cf8" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#818cf8" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
            <XAxis dataKey="date" stroke="#525252" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#525252" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value}`} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#171717', borderColor: '#404040', borderRadius: '12px', color: '#fff', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)' }}
              itemStyle={{ color: '#818cf8', fontWeight: 'bold' }}
            />
            <Area type="monotone" dataKey="price" stroke="#818cf8" strokeWidth={3} fillOpacity={1} fill="url(#historyGradient)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function Stat({ label, value, icon: Icon, color }: { label: string; value: number; icon: any; color: string }) {
  return (
    <motion.div 
      whileHover={{ y: -2 }}
      className="rounded-2xl border border-white/[0.04] bg-white/[0.02] p-4 transition-all hover:border-white/[0.08] hover:bg-white/[0.04]"
    >
      <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-2">
         <Icon className={`h-3 w-3 ${color}`} />
         {label}
      </div>
      <div className="text-xl font-black text-white tracking-tight">₹ {value.toLocaleString('en-IN')}</div>
    </motion.div>
  );
}

