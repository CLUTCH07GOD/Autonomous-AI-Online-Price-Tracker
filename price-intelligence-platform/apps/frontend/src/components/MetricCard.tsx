import { LucideIcon } from "lucide-react";
import { motion, useMotionTemplate, useMotionValue } from "framer-motion";

export function MetricCard({ label, value, icon: Icon, trend }: { label: string; value: string | number; icon: LucideIcon, trend?: string }) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  return (
    <div
      onMouseMove={handleMouseMove}
      className="group relative overflow-hidden rounded-2xl border border-white/10 bg-neutral-900 px-6 py-6 transition-all hover:border-white/20 hover:shadow-2xl hover:shadow-indigo-500/10"
    >
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition duration-300 group-hover:opacity-100"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              250px circle at ${mouseX}px ${mouseY}px,
              rgba(99, 102, 241, 0.15),
              transparent 80%
            )
          `,
        }}
      />
      <div className="relative z-10 flex items-center justify-between">
        <div className="text-sm font-medium tracking-wide text-neutral-400">{label}</div>
        <div className="rounded-lg bg-indigo-500/10 p-2 text-indigo-400 border border-indigo-500/20">
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <div className="relative z-10 mt-4 flex items-baseline gap-2">
        <div className="text-3xl font-bold tracking-tight text-white">{value}</div>
        {trend && (
          <div className="text-xs font-medium text-emerald-400">
            {trend}
          </div>
        )}
      </div>
    </div>
  );
}
