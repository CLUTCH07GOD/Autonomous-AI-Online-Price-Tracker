import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sun, Moon } from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { cn } from "../lib/utils";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="fixed bottom-6 right-6 z-[100] h-12 w-12 rounded-2xl backdrop-blur-xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center text-white shadow-glass hover:bg-white/[0.08] hover:scale-110 active:scale-95 transition-all group overflow-hidden"
    >
      {/* Background Glow */}
      <div className={cn(
        "absolute inset-0 opacity-20 transition-all duration-500",
        theme === "dark" ? "bg-indigo-500" : "bg-amber-500"
      )} />
      
      <AnimatePresence mode="wait" initial={false}>
        {theme === "dark" ? (
          <motion.div
            key="moon"
            initial={{ y: 20, rotate: 45, opacity: 0 }}
            animate={{ y: 0, rotate: 0, opacity: 1 }}
            exit={{ y: -20, rotate: -45, opacity: 0 }}
            transition={{ type: "spring", damping: 15, stiffness: 200 }}
          >
            <Moon className="h-5 w-5 text-indigo-400 group-hover:drop-shadow-[0_0_8px_rgba(129,140,248,0.8)]" />
          </motion.div>
        ) : (
          <motion.div
            key="sun"
            initial={{ y: 20, rotate: 45, opacity: 0 }}
            animate={{ y: 0, rotate: 0, opacity: 1 }}
            exit={{ y: -20, rotate: -45, opacity: 0 }}
            transition={{ type: "spring", damping: 15, stiffness: 200 }}
          >
            <Sun className="h-5 w-5 text-amber-400 group-hover:drop-shadow-[0_0_8px_rgba(251,191,36,0.8)]" />
          </motion.div>
        )}
      </AnimatePresence>
    </button>
  );
}
