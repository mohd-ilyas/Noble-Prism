import { motion } from "framer-motion";
import { Sparkles, TrendingUp, ShieldAlert, Brain, AlertTriangle } from "lucide-react";
import { useInsights } from "@/hooks/useApi";
import type { LucideIcon } from "lucide-react";

const fallbackInsights = [
  {
    tone: "danger" as const,
    title: "Emerging spoof pattern detected",
    body: "3 unknown agents attempted $50k+ transfers from EU IPs in the last 2h. Consider tightening identity attestation.",
    action: "Draft policy",
  },
  {
    tone: "primary" as const,
    title: "Cost optimization available",
    body: "Routing openai-buyer-07 compute settlements over USDC L2 could cut fees by 31%.",
    action: "Apply optimization",
  },
];

const toneIcon: Record<string, LucideIcon> = {
  danger: ShieldAlert,
  primary: TrendingUp,
  secondary: Brain,
  success: Sparkles,
  warning: AlertTriangle,
};

export function AiInsights() {
  const { data } = useInsights();
  const insights = data?.insights?.slice(0, 2) ?? fallbackInsights;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.1 }}
      className="glass-card overflow-hidden rounded-2xl border-l-4 border-l-accent-primary"
    >
      <div className="flex items-center gap-2 px-6 py-4">
        <div className="grid size-7 place-items-center rounded-md bg-accent-primary/15 text-accent-primary">
          <Sparkles className="size-3.5" />
        </div>
        <h3 className="font-display text-sm font-bold text-white">AI Insights</h3>
        <span className="ml-auto rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5 font-mono text-[10px] text-zinc-400">
          model v2.4
        </span>
      </div>
      <div className="divide-y divide-white/5">
        {insights.map((ins) => {
          const Icon = toneIcon[ins.tone] ?? Sparkles;
          const isDanger = ins.tone === "danger";
          return (
            <div key={ins.title} className="p-5">
              <div className="mb-2 flex items-center gap-2">
                <Icon
                  className={`size-3.5 ${isDanger ? "text-rose-400" : "text-accent-primary"}`}
                />
                <span className="text-xs font-semibold text-white">{ins.title}</span>
              </div>
              <p className="text-xs leading-relaxed text-zinc-400">{ins.body}</p>
              <button
                className={`mt-3 inline-flex items-center gap-1 rounded-md border px-2.5 py-1 text-[11px] font-semibold transition ${
                  isDanger
                    ? "border-rose-500/30 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20"
                    : "border-accent-primary/30 bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20"
                }`}
              >
                {ins.action} →
              </button>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
