import { motion } from "framer-motion";
import { ShieldCheck, Clock3, Leaf, TrendingUp } from "lucide-react";
import { useNegotiationProviders, useWorkflowStream } from "@/hooks/useApi";
import { useCommerceWebSocket } from "@/hooks/useCommerceWebSocket";

export function NegotiationDashboard() {
  const { data: fallbackProviders = [] } = useNegotiationProviders();
  const { data: fallbackWorkflows = [] } = useWorkflowStream();
  const wsMessages = useCommerceWebSocket();
  const snapshot = wsMessages.slice().reverse().find((message) => message.type === "commerce_snapshot");
  const providers = snapshot?.payload?.providers ?? fallbackProviders;
  const workflows = snapshot?.payload?.workflows ?? fallbackWorkflows;
  const selectedWorkflow = workflows[0];
  const liveTime = snapshot?.payload?.timestamp ? new Date(snapshot.payload.timestamp).toLocaleTimeString() : undefined;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.1 }}
      className="glass-card rounded-3xl p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-display text-lg font-bold text-white">Live Negotiation Dashboard</h3>
          <p className="text-xs text-zinc-500">Price, SLA, latency, reputation, and sustainability weighted in real time.</p>
        </div>
        <div className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-zinc-400">
          {selectedWorkflow?.status ?? "idle"}
          {liveTime ? ` • ${liveTime}` : ""}
        </div>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {providers.slice(0, 3).map((provider) => (
          <div key={provider.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-white">{provider.provider_name}</p>
                <p className="text-[11px] text-zinc-500">{provider.region}</p>
              </div>
              <div className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-300">
                {provider.availability}
              </div>
            </div>
            <div className="mt-4 grid gap-3 text-sm text-zinc-400">
              <div className="flex items-center justify-between"><span className="flex items-center gap-2"><TrendingUp className="size-3.5" /> Price</span><span className="font-medium text-white">${provider.price_per_unit.toFixed(2)}</span></div>
              <div className="flex items-center justify-between"><span className="flex items-center gap-2"><Clock3 className="size-3.5" /> SLA</span><span className="font-medium text-white">{provider.sla_days}d</span></div>
              <div className="flex items-center justify-between"><span className="flex items-center gap-2"><ShieldCheck className="size-3.5" /> Reputation</span><span className="font-medium text-white">{provider.reputation_score.toFixed(1)}</span></div>
              <div className="flex items-center justify-between"><span className="flex items-center gap-2"><Leaf className="size-3.5" /> Sustainability</span><span className="font-medium text-white">{provider.sustainability_score.toFixed(1)}</span></div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
