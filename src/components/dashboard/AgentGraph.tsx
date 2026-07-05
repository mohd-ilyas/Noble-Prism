import { motion } from "framer-motion";
import { useAgents } from "@/hooks/useApi";

export function AgentGraph() {
  const { data: agents = [] } = useAgents();

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.2 }}
      className="glass-card rounded-3xl p-6"
    >
      <h3 className="font-display text-lg font-bold text-white">Agent Graph</h3>
      <p className="mt-1 text-xs text-zinc-500">Connected providers, buyers, and mediators in the autonomous marketplace.</p>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {agents.slice(0, 6).map((agent, index) => (
          <div key={agent.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-white">{agent.name}</p>
              <span className="text-[10px] uppercase tracking-wider text-zinc-500">node {index + 1}</span>
            </div>
            <p className="mt-2 text-[11px] text-zinc-500">{agent.org} · {agent.reputation.toFixed(1)} reputation</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
