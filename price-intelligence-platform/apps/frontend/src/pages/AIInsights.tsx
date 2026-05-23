import React from "react";
import { motion } from "framer-motion";
import { 
  Brain, 
  TrendingDown, 
  TrendingUp, 
  Zap, 
  ArrowRight, 
  BarChart3, 
  Clock, 
  ShieldCheck, 
  Cpu, 
  Lightbulb,
  ArrowUpRight,
  Target
} from "lucide-react";
import { Prediction, Product, Recommendation, HeatmapCell } from "../types";
import { cn } from "../lib/utils";

interface AIInsightsProps {
  products: Product[];
  predictions: Prediction[];
  recommendations: Recommendation[];
  heatmap: HeatmapCell[];
  onPredict: (id: number) => void;
  onDiscount: (id: number) => void;
}

export function AIInsights({ products, predictions, recommendations, onPredict, onDiscount }: AIInsightsProps) {
  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-glow">
                <Brain className="h-6 w-6 text-white" />
            </div>
            AI Intelligence Hub
          </h2>
          <p className="text-neutral-400 mt-1">Predictive models and strategic buying insights.</p>
        </div>
        <div className="flex gap-2">
            <div className="px-4 py-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs font-bold text-indigo-400 flex items-center gap-2">
                <ShieldCheck className="h-4 w-4" />
                98.4% Prediction Accuracy
            </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Prediction Engine */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Clock className="h-5 w-5 text-neutral-500" />
                Price Prediction Timelines
            </h3>
          </div>

          <div className="space-y-4">
            {products.map((product) => {
              const prediction = predictions.find(p => p.product_id === product.id);
              return (
                <motion.div
                  key={product.id}
                  layout
                  className="glass-card-hover p-6 group"
                >
                  <div className="flex flex-col md:flex-row md:items-center gap-6">
                    <div className="h-16 w-16 rounded-2xl bg-white p-2 flex-shrink-0">
                      <img src={product.image_url || ""} alt="" className="h-full w-full object-contain" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-white truncate">{product.title}</h4>
                      <div className="flex items-center gap-4 mt-2">
                         <div>
                            <div className="text-[10px] text-neutral-500 font-bold uppercase">Current</div>
                            <div className="text-lg font-bold text-white">₹{product.current_best_price?.toLocaleString()}</div>
                         </div>
                         <div className="h-8 w-px bg-white/5" />
                         <div>
                            <div className="text-[10px] text-neutral-500 font-bold uppercase">Predicted</div>
                            <div className="text-lg font-bold text-indigo-400">
                                ₹{prediction ? Math.round(Number(prediction.predicted_price)).toLocaleString() : "---"}
                            </div>
                         </div>
                         <div className="h-8 w-px bg-white/5" />
                         <div>
                            <div className="text-[10px] text-neutral-500 font-bold uppercase">Trend</div>
                            <div className={cn(
                                "flex items-center gap-1 font-bold",
                                prediction?.trend === "down" ? "text-emerald-400" : "text-rose-400"
                            )}>
                                {prediction?.trend === "down" ? <TrendingDown className="h-4 w-4" /> : <TrendingUp className="h-4 w-4" />}
                                {prediction?.trend?.toUpperCase() || "STABLE"}
                            </div>
                         </div>
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-3">
                        <div className="flex items-center gap-2">
                            <div className="text-[10px] font-bold text-neutral-500 uppercase">Confidence</div>
                            <div className="w-24 bg-white/5 h-1.5 rounded-full overflow-hidden">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: prediction ? `${prediction.confidence * 100}%` : 0 }}
                                    className="h-full bg-indigo-500"
                                />
                            </div>
                            <div className="text-xs font-bold text-indigo-400">{prediction ? Math.round(prediction.confidence * 100) : 0}%</div>
                        </div>
                        <button
                          onClick={() => onPredict(product.id)}
                          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.03] border border-white/[0.06] text-xs font-bold text-white hover:bg-white/[0.06] transition-all"
                        >
                          <Cpu className="h-3.5 w-3.5" />
                          Refresh Model
                        </button>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Strategic Insights Sidebar */}
        <div className="space-y-8">
            <div className="rounded-[2.5rem] bg-indigo-600/10 border border-indigo-500/20 p-8 space-y-6">
                <div className="h-12 w-12 rounded-2xl bg-indigo-500 flex items-center justify-center text-white shadow-glow">
                    <Lightbulb className="h-6 w-6" />
                </div>
                <div>
                    <h3 className="text-xl font-bold text-white">Buying Strategy</h3>
                    <p className="text-sm text-indigo-200/70 mt-2">Our AI recommends holding off on large electronics purchases for 7 days. Market volatility is high.</p>
                </div>
                <div className="space-y-3">
                    {[
                        { label: "Optimal Window", val: "3-5 days" },
                        { label: "Market Sentiment", val: "Bearish" },
                        { label: "Volatility Index", val: "High" },
                    ].map(item => (
                        <div key={item.label} className="flex justify-between items-center py-2 border-b border-indigo-500/20 last:border-0">
                            <span className="text-xs font-medium text-indigo-300">{item.label}</span>
                            <span className="text-xs font-bold text-white uppercase">{item.val}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="space-y-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Target className="h-5 w-5 text-neutral-500" />
                    Strategic Recommendations
                </h3>
                {recommendations.slice(0, 3).map((rec, i) => (
                    <div key={i} className="p-4 glass-card-hover group">
                        <div className="flex items-center justify-between mb-3">
                            <div className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Action: {rec.type}</div>
                            <div className="text-[10px] text-neutral-500 font-bold">{rec.created_at ? new Date(rec.created_at).toLocaleDateString() : "Today"}</div>
                        </div>
                        <p className="text-sm text-neutral-300 font-medium leading-relaxed">{rec.content}</p>
                        <button className="mt-4 flex items-center gap-1 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors">
                            Apply Strategy
                            <ArrowRight className="h-3 w-3" />
                        </button>
                    </div>
                ))}
            </div>
        </div>
      </div>
    </div>
  );
}
