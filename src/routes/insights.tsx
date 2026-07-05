import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Sparkles, TrendingUp, AlertTriangle, Brain } from "lucide-react";
import { AppShell } from "@/components/dashboard/AppShell";
import { VolumeChart } from "@/components/dashboard/VolumeChart";
import { useInsights } from "@/hooks/useApi";
import type { LucideIcon } from "lucide-react";

export const Route = createFileRoute("/insights")({
  head: () => ({
    meta: [
      { title: "Insights — Aether" },
      {
        name: "description",
        content: "AI-driven anomaly detection and behavioral insights across the agent network.",
      },
    ],
  }),
  component: InsightsPage,
});

const fallbackInsights = [
  {
    icon: AlertTriangle,
    tone: "danger",
    title: "Unusual settlement cluster",
    body: "3 unknown agents attempted $147k in aggregate transfers to `compute-cluster-A` in the last 12 min — well above the 24h baseline of $2k. All blocked at gateway.",
    action: "Escalate to security",
  },
  {
    icon: TrendingUp,
    tone: "primary",
    title: "New corridor emerging",
    body: "Cross-org traffic between OpenAI ↔ Vertex grew 340% week-over-week. Consider a dedicated allowlist policy to reduce evaluation latency.",
    action: "Draft policy",
  },
  {
    icon: Brain,
    tone: "secondary",
    title: "Model drift detected",
    body: "Anomaly-v2.4 false-positive rate rose from 0.4% → 1.1% over the last 24h. Retrain queued for 03:00 UTC with 48h fresh telemetry.",
    action: "View training run",
  },
  {
    icon: Sparkles,
    tone: "success",
    title: "Reputation uplift",
    body: "12 agents crossed the 95.0 reputation threshold this week — now eligible for the fast-path settlement lane (avg −6 ms latency).",
    action: "Notify orgs",
  },
];

const toneClass: Record<string, string> = {
  danger: "border-rose-500/30 bg-rose-500/5 text-rose-300",
  primary: "border-accent-primary/30 bg-accent-primary/5 text-accent-primary",
  secondary: "border-accent-secondary/30 bg-accent-secondary/5 text-accent-secondary",
  success: "border-emerald-500/30 bg-emerald-500/5 text-emerald-300",
};

const toneIcon: Record<string, LucideIcon> = {
  danger: AlertTriangle,
  primary: TrendingUp,
  secondary: Brain,
  success: Sparkles,
};

function InsightsPage() {
  const { data, isError } = useInsights();
  const insights = data?.insights ?? fallbackInsights;

  return (
    <AppShell breadcrumb="Insights">
      <header className="flex flex-col gap-2">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-accent-primary">
          AI Copilot
        </span>
        <h1 className="font-display text-4xl font-bold text-white">Signals & Anomalies</h1>
        <p className="max-w-2xl text-sm text-zinc-400">
          Continuously synthesized insights across every agent, transaction and policy decision —
          surfaced before they become incidents.
        </p>
        {isError && (
          <p className="text-xs text-amber-400">⚠ Could not reach backend — showing cached data.</p>
        )}
      </header>

      <VolumeChart />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {insights.map((it, i) => {
          const Icon = (it as { icon?: LucideIcon }).icon ?? toneIcon[it.tone] ?? Sparkles;
          return (
            <motion.div
              key={it.title}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              className="glass-card glow-hover rounded-2xl p-5"
            >
              <div className="flex items-start gap-3">
                <div
                  className={`grid size-10 shrink-0 place-items-center rounded-xl border ${toneClass[it.tone] ?? toneClass.primary}`}
                >
                  <Icon className="size-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-display text-base font-bold text-white">{it.title}</h3>
                  <p className="mt-1.5 text-xs leading-relaxed text-zinc-400">{it.body}</p>
                  <button className="mt-4 text-xs font-semibold text-accent-primary transition hover:text-white">
                    {it.action} →
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </AppShell>
  );
}
