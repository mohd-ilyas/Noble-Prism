import { motion } from "framer-motion";
import { useInsights } from "@/hooks/useApi";
import { eventsFeed as mockEventsFeed } from "@/lib/mock-data";

const dotColor: Record<string, string> = {
  success: "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.7)]",
  warning: "bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.7)]",
  danger: "bg-rose-500 shadow-[0_0_10px_rgba(239,68,68,0.7)]",
  primary: "bg-accent-primary shadow-[0_0_10px_rgba(59,130,246,0.7)]",
  secondary: "bg-accent-secondary shadow-[0_0_10px_rgba(168,85,247,0.7)]",
};

export function EventsTimeline() {
  const { data } = useInsights();
  const events = data?.events ?? mockEventsFeed;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.2 }}
      className="glass-card rounded-2xl p-6"
    >
      <div className="mb-5 flex items-center justify-between">
        <h3 className="font-display text-base font-bold text-white">Recent Events</h3>
        <span className="text-[10px] font-medium text-zinc-500">last 15 min</span>
      </div>
      <div className="relative space-y-4">
        <div className="absolute bottom-2 left-[5px] top-2 w-px bg-white/5" />
        {events.map((e, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.3 + i * 0.08 }}
            className="relative flex gap-3 pl-1"
          >
            <span
              className={`relative z-10 mt-1.5 size-2.5 shrink-0 rounded-full ${dotColor[e.dot] ?? dotColor.primary}`}
            />
            <div className="min-w-0">
              <p className="text-xs font-medium text-white">{e.title}</p>
              <p className="mt-0.5 text-[11px] text-zinc-500">{e.detail}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
