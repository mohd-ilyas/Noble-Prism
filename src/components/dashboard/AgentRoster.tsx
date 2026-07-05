import { motion } from "framer-motion";
import { useAgents } from "@/hooks/useApi";
import { agents as mockAgents } from "@/lib/mock-data";

const statusDot: Record<string, string> = {
  online: "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.7)]",
  idle: "bg-amber-500",
  offline: "bg-zinc-600",
};

export function AgentRoster() {
  const { data } = useAgents();
  const agents = data ?? mockAgents;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.15 }}
      className="glass-card rounded-2xl p-6"
    >
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="font-display text-base font-bold text-white">Top Agents</h3>
          <p className="text-[11px] text-zinc-500">by reputation · today</p>
        </div>
        <button className="text-[11px] font-semibold text-accent-primary hover:underline">
          View all →
        </button>
      </div>

      <div className="space-y-3">
        {agents.slice(0, 5).map((a, i) => (
          <div key={a.id} className="flex items-center gap-3">
            <div className="relative">
              <div className="grid size-9 place-items-center rounded-lg bg-gradient-to-br from-white/10 to-white/[0.02] font-mono text-[11px] font-bold text-zinc-300">
                {a.name.slice(0, 2).toUpperCase()}
              </div>
              <span
                className={`absolute -bottom-0.5 -right-0.5 size-2.5 rounded-full ring-2 ring-[#121214] ${statusDot[a.status]}`}
              />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-white">{a.name}</p>
              <p className="text-[10px] text-zinc-500">
                {a.org} · ${a.spendToday.toLocaleString()} today
              </p>
            </div>
            <div className="text-right">
              <div className="font-mono text-xs font-semibold text-white">
                {a.reputation.toFixed(1)}
              </div>
              <div className="h-1 w-14 overflow-hidden rounded-full bg-white/5">
                <motion.div
                  className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                  initial={{ width: 0 }}
                  animate={{ width: `${a.reputation}%` }}
                  transition={{ duration: 1.2, delay: 0.2 + i * 0.08, ease: [0.16, 1, 0.3, 1] }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
