import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../components/AuthContext";
import { Brain, ArrowRight, Github, Mail, Lock, User as UserIcon, Sparkles } from "lucide-react";
import { ParticleField } from "../components/ParticleBackground";

export function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { login, signup } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await signup(name, email, password);
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#06060f] flex items-center justify-center p-4 sm:p-6">
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.018)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.018)_1px,transparent_1px)] bg-[size:56px_56px] [mask-image:linear-gradient(to_bottom,#000_20%,transparent_100%)]" />
        <ParticleField count={24} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.92 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Logo & Title */}
        <div className="flex flex-col items-center mb-8 text-center">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", damping: 12, stiffness: 200, delay: 0.2 }}
            className="relative mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-fuchsia-500 animate-glow-pulse"
          >
            <Brain className="relative z-10 h-8 w-8 text-white" />
            {/* Rotating glow ring */}
            <div className="pointer-events-none absolute -inset-2 rounded-3xl border border-indigo-500/20 animate-spin" style={{ animationDuration: "8s" }} />
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-3xl sm:text-4xl font-black tracking-tight text-white leading-tight"
          >
            Price Intel
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent"> AI</span>
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-neutral-500 mt-3 text-center text-sm flex max-w-xs items-center justify-center gap-2 leading-relaxed"
          >
            <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
            AI-powered intelligence at your fingertips
          </motion.p>
        </div>

        {/* Glass Login Card */}
        <motion.div
          className="rounded-3xl border border-white/[0.08] backdrop-blur-2xl p-5 sm:p-7 relative overflow-hidden group"
          whileHover={{ borderColor: "rgba(99,102,241,0.15)" }}
        >
          {/* Glass background layers */}
          <div className="absolute inset-0 bg-gradient-to-b from-white/[0.05] to-white/[0.02] pointer-events-none" />
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/[0.03] to-purple-500/[0.02] pointer-events-none" />
          
          {/* Animated border glow */}
          <div className="absolute inset-0 rounded-[2rem] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
            style={{ boxShadow: "inset 0 0 30px rgba(99,102,241,0.05), 0 0 40px rgba(99,102,241,0.05)" }}
          />

          {/* Shine sweep */}
          <div className="absolute inset-0 overflow-hidden rounded-[2rem] pointer-events-none">
            <div className="absolute top-0 -left-full w-1/2 h-full bg-gradient-to-r from-transparent via-white/[0.04] to-transparent skew-x-[-15deg] group-hover:left-[150%] transition-all duration-1000 ease-in-out" />
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
            <AnimatePresence mode="wait">
              {!isLogin && (
                <motion.div
                  initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                  animate={{ opacity: 1, height: "auto", marginBottom: 0 }}
                  exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-2"
                >
                  <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 px-1">Full Name</label>
                  <div className="relative group/input">
                    <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-600 group-focus-within/input:text-indigo-400 transition-colors" />
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="glass-input w-full pl-11"
                      placeholder="John Doe"
                      required={!isLogin}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500 px-1">Email Address</label>
              <div className="relative group/input">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-600 group-focus-within/input:text-indigo-400 transition-colors" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="glass-input w-full pl-11"
                  placeholder="name@example.com"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between px-1">
                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-500">Password</label>
                {isLogin && (
                  <button type="button" className="text-[10px] font-bold uppercase tracking-widest text-indigo-400/70 hover:text-indigo-300 transition-colors">Forgot?</button>
                )}
              </div>
              <div className="relative group/input">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-600 group-focus-within/input:text-indigo-400 transition-colors" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="glass-input w-full pl-11"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-2 text-xs font-medium text-rose-400 px-1 py-2 rounded-xl bg-rose-500/[0.06] border border-rose-500/10"
              >
                <div className="h-1.5 w-1.5 rounded-full bg-rose-400 flex-shrink-0" />
                {error}
              </motion.div>
            )}

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              className="w-full group/btn relative flex items-center justify-center gap-2 rounded-2xl px-4 py-4 font-bold text-white transition-all disabled:opacity-50 overflow-hidden"
              style={{
                background: "linear-gradient(135deg, rgba(99,102,241,0.9), rgba(139,92,246,0.9))",
                boxShadow: "0 0 25px rgba(99,102,241,0.3), 0 4px 15px rgba(0,0,0,0.3)",
              }}
            >
              {/* Animated gradient sweep */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.08] to-transparent translate-x-[-200%] group-hover/btn:translate-x-[200%] transition-transform duration-1000 ease-in-out" />
              
              {loading ? (
                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {isLogin ? "Sign In to Dashboard" : "Create Account"}
                  <ArrowRight className="h-4 w-4 group-hover/btn:translate-x-1 transition-transform" />
                </>
              )}
            </motion.button>
          </form>

          {/* Divider */}
          <div className="mt-8 flex flex-col gap-4 relative z-10">
            <div className="relative">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/[0.05]" /></div>
              <div className="relative flex justify-center text-[9px] uppercase tracking-[0.2em] font-black">
                <span className="px-4 text-neutral-600" style={{ backgroundColor: "rgba(10,10,20,0.8)" }}>Or continue with</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button className="flex items-center justify-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.02] py-3 text-sm font-medium text-neutral-400 transition-all hover:bg-white/[0.05] hover:text-white hover:border-white/[0.1]">
                <Github className="h-4 w-4" />
                Github
              </button>
              <button className="flex items-center justify-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.02] py-3 text-sm font-medium text-neutral-400 transition-all hover:bg-white/[0.05] hover:text-white hover:border-white/[0.1]">
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor"><path d="M12.48 10.92v3.28h7.84c-.24 1.84-2.21 5.39-7.84 5.39-4.84 0-8.79-4.01-8.79-8.97s3.95-8.97 8.79-8.97c2.75 0 4.59 1.17 5.65 2.18l2.58-2.49c-1.66-1.55-3.82-2.51-8.23-2.51-6.63 0-12 5.37-12 12s5.37 12 12 12c6.93 0 11.53-4.87 11.53-11.72 0-.79-.08-1.4-.21-2h-11.32z"/></svg>
                Google
              </button>
            </div>
          </div>
        </motion.div>

        {/* Toggle */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 text-center"
        >
          <button
            onClick={() => { setIsLogin(!isLogin); setError(""); }}
            className="text-sm font-medium text-neutral-600 hover:text-neutral-300 transition-colors"
          >
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <span className="text-indigo-400 font-bold hover:text-indigo-300 transition-colors">{isLogin ? "Sign up free" : "Log in"}</span>
          </button>
        </motion.div>
      </motion.div>
    </div>
  );
}
