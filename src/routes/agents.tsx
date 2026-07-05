import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Circle, TrendingUp, Shield, Search, Lock, Unlock } from "lucide-react";
import { AppShell } from "@/components/dashboard/AppShell";
import { useAgents, useActivateKillSwitch, useReleaseKillSwitch } from "@/hooks/useApi";
import { agents as mockAgents } from "@/lib/mock-data";
import { toast } from "sonner";

export const Route = createFileRoute("/agents")({
  head: () => ({
    meta: [
      { title: "Agents — Aether" },
      {
        name: "description",
        content: "Directory of autonomous agents connected to the Aether protocol.",
      },
    ],
  }),
  component: AgentsPage,
});

const statusColor: Record<string, string> = {
  online: "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.7)]",
  idle: "bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.7)]",
  offline: "bg-zinc-600",
};

function AgentsPage() {
  const { data, isLoading, isError } = useAgents();
  const freeze = useActivateKillSwitch();
  const release = useReleaseKillSwitch();
  const [search, setSearch] = useState("");
  const [freezeTarget, setFreezeTarget] = useState<string | null>(null);
  const [freezeReason, setFreezeReason] = useState("");

  const allAgents = data ?? mockAgents;
  const agents = search
    ? allAgents.filter(
        (a) =>
          a.name.toLowerCase().includes(search.toLowerCase()) ||
          a.org.toLowerCase().includes(search.toLowerCase()),
      )
    : allAgents;

  const handleFreeze = async (agentId: string) => {
    if (!freezeReason.trim()) return;
    try {
      await freeze.mutateAsync({ agentId, reason: freezeReason });
      toast.success("Agent frozen successfully");
      setFreezeTarget(null);
      setFreezeReason("");
    } catch {
      toast.error("Failed to freeze agent");
    }
  };

  const handleRelease = async (agentId: string) => {
    try {
      await release.mutateAsync({ agentId });
      toast.success("Agent released");
    } catch {
      toast.error("Failed to release agent");
    }
  };

  return (
    <AppShell breadcrumb="Agents">
      <header className="flex flex-col gap-2">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-accent-primary">
          Directory
        </span>
        <h1 className="font-display text-4xl font-bold text-white">Connected Agents</h1>
        <p className="max-w-2xl text-sm text-zinc-400">
          Every autonomous agent authenticated against the Aether registry. Reputation is calculated
          from settlement success, policy compliance, and peer attestation over a rolling 30 day
          window.
        </p>
        {isError && (
          <p className="text-xs text-amber-400">⚠ Could not reach backend — showing cached data.</p>
        )}
      </header>

      <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-2.5">
        <Search className="size-4 text-zinc-500" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search agents by name or org…"
          className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-zinc-600"
        />
        {search && (
          <button onClick={() => setSearch("")} className="text-xs text-zinc-500 hover:text-white">
            Clear
          </button>
        )}
      </div>

      {isLoading && !data ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card animate-pulse rounded-2xl p-5 h-40" />
          ))}
        </div>
      ) : agents.length === 0 ? (
        <div className="glass-card rounded-2xl p-10 text-center text-zinc-500">
          No agents found{search ? ` matching "${search}"` : ""}.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {agents.map((a, i) => (
            <motion.div
              key={a.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className={`glass-card glow-hover rounded-2xl p-5 ${(a as { is_frozen?: boolean }).is_frozen ? "border border-rose-500/30" : ""}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="grid size-11 place-items-center rounded-xl bg-gradient-to-br from-accent-primary/30 to-accent-secondary/30 text-white">
                    <Cpu className="size-5" />
                  </div>
                  <div>
                    <div className="font-mono text-sm font-semibold text-white">{a.name}</div>
                    <div className="text-[11px] uppercase tracking-wider text-zinc-500">
                      {a.org}
                    </div>
                  </div>
                </div>
                <span className="mt-1.5 flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-wider text-zinc-400">
                  <Circle
                    className={`size-2 rounded-full ${statusColor[a.status] ?? statusColor.offline}`}
                    fill="currentColor"
                  />
                  {(a as { is_frozen?: boolean }).is_frozen ? "frozen" : a.status}
                </span>
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-white/5 bg-white/[0.02] p-3">
                  <div className="flex items-center gap-1 text-[10px] uppercase tracking-wider text-zinc-500">
                    <Shield className="size-3" /> Reputation
                  </div>
                  <div className="mt-1 font-display text-xl font-bold text-white">
                    {a.reputation.toFixed(1)}
                  </div>
                </div>
                <div className="rounded-lg border border-white/5 bg-white/[0.02] p-3">
                  <div className="flex items-center gap-1 text-[10px] uppercase tracking-wider text-zinc-500">
                    <TrendingUp className="size-3" /> Spend 24h
                  </div>
                  <div className="mt-1 font-display text-xl font-bold text-white">
                    ${a.spendToday.toLocaleString()}
                  </div>
                </div>
              </div>

              <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                  style={{ width: `${a.reputation}%` }}
                />
              </div>

              {data && (
                <div className="mt-4 flex gap-2">
                  {(a as { is_frozen?: boolean }).is_frozen ? (
                    <button
                      onClick={() => handleRelease(a.id)}
                      disabled={release.isPending}
                      className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-300 transition hover:bg-emerald-500/20 disabled:opacity-50"
                    >
                      <Unlock className="size-3" /> Release
                    </button>
                  ) : (
                    <button
                      onClick={() => setFreezeTarget(a.id)}
                      className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-1.5 text-xs font-semibold text-rose-300 transition hover:bg-rose-500/20"
                    >
                      <Lock className="size-3" /> Freeze
                    </button>
                  )}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}

      {/* Freeze confirmation modal */}
      {freezeTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="glass-card w-full max-w-sm rounded-2xl p-6">
            <h2 className="font-display text-lg font-bold text-white">Freeze Agent</h2>
            <p className="mt-1 text-sm text-zinc-400">
              This will immediately block all transactions from this agent.
            </p>
            <label className="mt-4 block">
              <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
                Reason
              </div>
              <input
                value={freezeReason}
                onChange={(e) => setFreezeReason(e.target.value)}
                placeholder="e.g. Suspicious spending pattern"
                className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-accent-primary/50"
              />
            </label>
            <div className="mt-4 flex justify-end gap-3">
              <button
                onClick={() => { setFreezeTarget(null); setFreezeReason(""); }}
                className="rounded-lg border border-white/10 px-4 py-2 text-sm text-zinc-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() => handleFreeze(freezeTarget)}
                disabled={!freezeReason.trim() || freeze.isPending}
                className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-600 disabled:opacity-50"
              >
                {freeze.isPending ? "Freezing…" : "Confirm Freeze"}
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
