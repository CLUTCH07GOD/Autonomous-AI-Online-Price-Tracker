import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  BookOpen, 
  GitMerge, 
  Cpu, 
  Terminal, 
  ArrowRight, 
  Play, 
  CheckCircle2, 
  Layers, 
  Activity, 
  HelpCircle, 
  RefreshCw, 
  AlertTriangle 
} from "lucide-react";
import { api } from "../lib/api";
import { cn } from "../lib/utils";

interface IntegrationPoint {
  feature: string;
  file: string;
  status: string;
}

interface ReferenceItem {
  id: string;
  title: string;
  description: string;
  path: string;
  features: string[];
  tech_stack: string[];
  integration_points: IntegrationPoint[];
}

export function ReferenceHub() {
  const [references, setReferences] = useState<ReferenceItem[]>([]);
  const [selectedRef, setSelectedRef] = useState<ReferenceItem | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Sandbox State
  const [rawText, setRawText] = useState("Was € 1.249,99 Now € 999,99 (Save 20%)");
  const [localeHint, setLocaleHint] = useState("AUTO");
  const [parseResult, setParseResult] = useState<any>(null);
  const [parsing, setParsing] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    async function loadRefs() {
      try {
        setLoading(true);
        const data = await api.references();
        setReferences(data || []);
        if (data && data.length > 0) {
          setSelectedRef(data[0]);
        }
      } catch (err) {
        console.error("Failed to load reference items:", err);
      } finally {
        setLoading(false);
      }
    }
    loadRefs();
  }, []);

  async function handleTestParse() {
    if (!rawText.trim()) return;
    try {
      setParsing(true);
      setErrorMsg("");
      setParseResult(null);
      const res = await api.parseReference(rawText, localeHint);
      setParseResult(res);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to normalize string");
    } finally {
      setParsing(false);
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08
      }
    }
  };

  const itemVariants = {
    hidden: { y: 15, opacity: 0 },
    show: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="h-8 w-8 animate-spin text-indigo-500" />
          <p className="text-sm font-bold text-neutral-400">Syncing references repository...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-16">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-glow">
              <BookOpen className="h-5 w-5 text-white" />
            </div>
            Reference Engineering Hub
          </h2>
          <p className="text-neutral-400 mt-1">Explore integration lineage, technology stacks, and merged scrapers derived from our reference models.</p>
        </div>
        <div className="flex gap-2">
          <div className="px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs font-bold text-emerald-400 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            4 Active Repositories Merged
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Left Side: Repos List & Active Repo Details */}
        <div className="xl:col-span-2 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {references.map((ref) => {
              const isSelected = selectedRef?.id === ref.id;
              return (
                <button
                  key={ref.id}
                  onClick={() => setSelectedRef(ref)}
                  className={cn(
                    "text-left p-5 rounded-2xl border transition-all duration-300 relative overflow-hidden group",
                    isSelected 
                      ? "bg-white/[0.04] border-indigo-500/40 shadow-glow-sm" 
                      : "bg-white/[0.01] border-white/[0.05] hover:bg-white/[0.02] hover:border-white/10"
                  )}
                >
                  <div className="flex items-start gap-4">
                    <div className={cn(
                      "h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors",
                      isSelected ? "bg-indigo-500 text-white shadow-glow" : "bg-white/[0.04] text-neutral-400 group-hover:text-neutral-200"
                    )}>
                      <Layers className="h-4 w-4" />
                    </div>
                    <div className="space-y-1">
                      <h4 className="font-bold text-sm text-white group-hover:text-indigo-300 transition-colors">{ref.title}</h4>
                      <p className="text-xs text-neutral-400 line-clamp-1">{ref.description}</p>
                    </div>
                  </div>
                  {isSelected && (
                    <div className="absolute right-3 top-3 h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
                  )}
                </button>
              );
            })}
          </div>

          {/* Active Reference Detail Glass Card */}
          <AnimatePresence mode="wait">
            {selectedRef && (
              <motion.div
                key={selectedRef.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="glass-card p-8 space-y-6 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-indigo-500/5 rounded-full blur-[100px] -mr-20 -mt-20 pointer-events-none" />
                
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/[0.04]">
                  <div>
                    <span className="text-[10px] uppercase font-black tracking-widest text-indigo-400">Reference Architecture</span>
                    <h3 className="text-xl font-bold text-white mt-1">{selectedRef.title}</h3>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono bg-black/40 border border-white/5 text-neutral-400 px-3 py-1.5 rounded-lg">
                    <Terminal className="h-3.5 w-3.5" />
                    {selectedRef.path}
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest">Description</h4>
                  <p className="text-sm text-neutral-300 leading-relaxed font-medium">{selectedRef.description}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Features */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest">Key Core Features</h4>
                    <ul className="space-y-2">
                      {selectedRef.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-neutral-300 font-medium">
                          <CheckCircle2 className="h-4.5 w-4.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Tech Stack */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest">Technology Stack</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedRef.tech_stack.map((tech) => (
                        <span key={tech} className="px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.06] text-xs font-bold text-neutral-300">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Lineage Mapping */}
                <div className="space-y-4 pt-4 border-t border-white/[0.04]">
                  <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest flex items-center gap-2">
                    <GitMerge className="h-4 w-4 text-indigo-400" />
                    Codebase Lineage Integration
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedRef.integration_points.map((pt, idx) => (
                      <div key={idx} className="p-4 rounded-2xl bg-white/[0.01] border border-white/[0.04] flex flex-col justify-between gap-3 hover:border-white/[0.08] transition-colors">
                        <div>
                          <div className="text-[10px] uppercase font-bold text-neutral-500">Platform Feature</div>
                          <div className="text-sm font-bold text-white mt-0.5">{pt.feature}</div>
                        </div>
                        <div className="flex items-center justify-between mt-1 pt-2 border-t border-white/[0.03]">
                          <span className="text-xs font-mono text-indigo-400/80 truncate max-w-[200px]" title={pt.file}>{pt.file.split('/').pop()}</span>
                          <span className="text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                            {pt.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </motion.div>
            )}
          </AnimatePresence>

        </div>

        {/* Right Side: Interactive Scraper Sandbox Playground */}
        <div className="space-y-6">
          <div className="glass-card p-6 space-y-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-[150px] h-[150px] bg-purple-500/5 rounded-full blur-[80px] -mr-10 -mt-10 pointer-events-none" />
            
            <div className="pb-4 border-b border-white/[0.04]">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Activity className="h-5 w-5 text-indigo-400" />
                Scraper Sandbox Playground
              </h3>
              <p className="text-xs text-neutral-400 mt-1">Test messy, localized pricing strings against our production-merged normalization heuristics.</p>
            </div>

            {/* Input Form */}
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-[10px] font-bold uppercase text-neutral-500">Raw Pricing Text String</label>
                <input
                  type="text"
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="e.g. Was $1,299.99 Now $999.00 (Save 23%)"
                  className="w-full h-11 px-4 rounded-xl border border-white/[0.06] bg-black/40 text-sm font-medium text-white focus:outline-none focus:border-indigo-500/40"
                />
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-bold uppercase text-neutral-500">Locale Interception Hint</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: "AUTO", desc: "Auto-Detect Heuristics" },
                    { id: "US", desc: "US/UK ($1,234.56)" },
                    { id: "EU", desc: "EU (1.234,56)" }
                  ].map((loc) => (
                    <button
                      key={loc.id}
                      onClick={() => setLocaleHint(loc.id)}
                      className={cn(
                        "py-2 rounded-xl text-xs font-bold border transition-colors",
                        localeHint === loc.id 
                          ? "bg-indigo-500/10 border-indigo-500/30 text-indigo-400" 
                          : "bg-white/[0.02] border-white/[0.05] text-neutral-400 hover:text-white"
                      )}
                    >
                      {loc.id}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleTestParse}
                disabled={parsing || !rawText.trim()}
                className="w-full h-11 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-sm font-bold text-white flex items-center justify-center gap-2 shadow-glow hover:shadow-glow-lg transition-all disabled:opacity-50"
              >
                {parsing ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4 fill-white" />
                )}
                Run Normalization Test
              </button>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/25 flex items-start gap-3">
                <AlertTriangle className="h-4 w-4 text-rose-400 mt-0.5 flex-shrink-0" />
                <p className="text-xs font-medium text-rose-300 leading-relaxed">{errorMsg}</p>
              </div>
            )}

            {/* Parse Sandbox Results */}
            <AnimatePresence>
              {parseResult && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="p-5 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-4"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-white/[0.04]">
                    <span className="text-[10px] font-bold uppercase text-neutral-400">Normalization Result</span>
                    <span className="text-[9px] font-black uppercase bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">Success</span>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <div className="text-[9px] uppercase font-bold text-neutral-500">Heuristics Pre-Cleaned Token</div>
                      <div className="text-xs font-mono text-neutral-300 mt-0.5 break-all">{parseResult.cleaned_marketing}</div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-[9px] uppercase font-bold text-neutral-500">Normalized Price</div>
                        <div className="text-lg font-bold text-white mt-0.5">
                          {parseResult.parsed_price !== null ? (
                            <span>{parseResult.currency === "INR" ? "₹" : parseResult.currency === "EUR" ? "€" : "$"}{parseResult.parsed_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                          ) : (
                            <span className="text-neutral-500 font-medium text-sm">Not detected</span>
                          )}
                        </div>
                      </div>
                      
                      <div>
                        <div className="text-[9px] uppercase font-bold text-neutral-500">Detected Currency</div>
                        <div className="text-lg font-bold text-indigo-400 mt-0.5">
                          {parseResult.currency || "None"}
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

          </div>

          {/* Sandbox Info */}
          <div className="p-5 rounded-[2rem] bg-indigo-600/10 border border-indigo-500/20 space-y-4">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <HelpCircle className="h-4.5 w-4.5 text-indigo-400" />
              How Normalization Works
            </h4>
            <p className="text-xs text-indigo-200/70 leading-relaxed font-medium">
              E-commerce portals represent price lists in highly noisy formats (e.g. <code className="text-indigo-300">Was $129.99 (Save 20%) Now $99.99</code> or <code className="text-indigo-300">1.299,00 €</code>).
            </p>
            <p className="text-xs text-indigo-200/70 leading-relaxed font-medium">
              Our reference parser removes all marketing elements, intercepts the numeric value, handles decimal separators correctly based on the locale hint, and returns a high-precision decimal token for data validation.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
