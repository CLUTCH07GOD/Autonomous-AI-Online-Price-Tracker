import { X, CheckCircle2, AlertCircle, Info, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export type ToastMessage = { id: number; type: "success" | "error" | "info"; text: string };

export function ToastStack({ messages, onDismiss }: { messages: ToastMessage[]; onDismiss: (id: number) => void }) {
  return (
    <div className="fixed right-4 top-4 z-[100] space-y-3 flex flex-col items-end">
      <AnimatePresence mode="popLayout">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            layout
            initial={{ opacity: 0, x: 30, scale: 0.9, filter: "blur(4px)" }}
            animate={{ opacity: 1, x: 0, scale: 1, filter: "blur(0px)" }}
            exit={{ opacity: 0, x: 20, scale: 0.9, filter: "blur(4px)" }}
            className={`group flex max-w-sm items-center gap-3 rounded-2xl backdrop-blur-2xl px-5 py-3.5 text-sm shadow-glass border ${
              message.type === "error" 
                ? "border-rose-500/20 bg-rose-950/40 text-rose-200" 
                : message.type === "success" 
                ? "border-emerald-500/20 bg-emerald-950/40 text-emerald-200" 
                : "border-white/[0.08] bg-white/[0.03] text-neutral-200"
            }`}
          >
            {message.type === "success" && <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0" />}
            {message.type === "error" && <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0" />}
            {message.type === "info" && <Info className="h-5 w-5 text-indigo-400 flex-shrink-0" />}
            
            <div className="min-w-0 flex-1 font-medium">{message.text}</div>
            
            <button 
              onClick={() => onDismiss(message.id)} 
              className="rounded-lg p-1.5 transition-all hover:bg-white/[0.06] opacity-0 group-hover:opacity-100" 
              title="Dismiss"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

export function LoadingBlock({ label = "Analyzing market intelligence..." }: { label?: string }) {
  return (
    <div className="glass-card p-8 relative overflow-hidden">
      {/* Progress bar */}
      <div className="absolute top-0 left-0 h-[2px] w-full bg-white/[0.03] overflow-hidden rounded-t-3xl">
        <motion.div 
          initial={{ x: "-100%" }}
          animate={{ x: "100%" }}
          transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
          className="h-full w-1/3 rounded-full"
          style={{ 
            background: "linear-gradient(90deg, transparent, rgba(99,102,241,0.8), transparent)",
            boxShadow: "0 0 15px rgba(99,102,241,0.6)"
          }}
        />
      </div>
      
      <div className="flex items-center gap-4 mb-8">
        <div className="h-12 w-12 rounded-2xl bg-white/[0.04] animate-pulse" />
        <div className="space-y-2.5">
          <div className="h-4 w-48 rounded-lg bg-white/[0.04] animate-pulse" />
          <div className="h-3 w-32 rounded-lg bg-white/[0.03] animate-pulse" />
        </div>
      </div>
      
      <div className="grid gap-6 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <motion.div 
            key={i} 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="space-y-3 rounded-2xl border border-white/[0.04] bg-white/[0.02] p-4"
          >
            <div className="h-4 w-2/3 rounded-lg bg-white/[0.04] animate-pulse" />
            <div className="h-10 w-full rounded-xl bg-white/[0.03] animate-pulse" />
          </motion.div>
        ))}
      </div>
      
      <div className="mt-8 flex items-center justify-center gap-3 text-sm font-medium text-neutral-500">
        <div className="relative">
          <Loader2 className="h-5 w-5 animate-spin text-indigo-500" />
          <div className="absolute inset-0 rounded-full animate-ping opacity-20 bg-indigo-500" />
        </div>
        {label}
      </div>
    </div>
  );
}
