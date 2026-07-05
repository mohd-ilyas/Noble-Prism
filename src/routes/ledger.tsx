import * as React from "react";
import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import { AppShell } from "@/components/dashboard/AppShell";
import { useLedger } from "@/hooks/useApi";
import { transactions as mockTransactions } from "@/lib/mock-data";
import type { LedgerEntry } from "@/lib/api";

export const Route = createFileRoute("/ledger")({
  head: () => ({
    meta: [
      { title: "Ledger — Aether" },
      { name: "description", content: "Tamper-evident ledger of all agent-to-agent settlements." },
    ],
  }),
  component: LedgerPage,
});

type TxStatus = "approved" | "blocked" | "escalated";

const statusIcon: Record<TxStatus, React.ReactNode> = {
  approved: <CheckCircle2 className="size-3.5 text-emerald-400" />,
  blocked: <XCircle className="size-3.5 text-rose-400" />,
  escalated: <AlertTriangle className="size-3.5 text-amber-400" />,
};

const statusStyle: Record<TxStatus, string> = {
  approved: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  blocked: "border-rose-500/30 bg-rose-500/10 text-rose-300",
  escalated: "border-amber-500/30 bg-amber-500/10 text-amber-300",
};

function normaliseStatus(s: string): TxStatus {
  if (s === "approved") return "approved";
  if (s === "blocked") return "blocked";
  return "escalated";
}

function LedgerPage() {
  const { data, isLoading, isError } = useLedger(50);

  // Map live LedgerEntry shape to the display shape; fall back to mock data
  const rows = React.useMemo(() => {
    if (data && data.length > 0) {
      return data.map((e: LedgerEntry) => ({
        id: e.display_id ?? e.transaction_id,
        from: e.from,
        to: e.to,
        amount: e.amount,
        currency: e.currency,
        status: normaliseStatus(e.status),
        riskScore: e.riskScore ?? e.risk_score ?? 0,
        timestamp: e.timestamp,
        latencyMs: e.latencyMs ?? e.latency_ms ?? 0,
      }));
    }
    return mockTransactions.map((t) => ({
      id: t.id,
      from: t.from,
      to: t.to,
      amount: t.amount,
      currency: t.currency,
      status: t.status,
      riskScore: t.riskScore,
      timestamp: t.timestamp,
      latencyMs: t.latencyMs,
    }));
  }, [data]);

  return (
    <AppShell breadcrumb="Ledger">
      <header className="flex flex-col gap-2">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-accent-primary">
          Immutable log
        </span>
        <h1 className="font-display text-4xl font-bold text-white">Settlement Ledger</h1>
        <p className="max-w-2xl text-sm text-zinc-400">
          Every settled transaction anchored with a tamper-evident receipt. Ledger root checkpointed
          to L2 every 90 seconds.
        </p>
        {isError && (
          <p className="text-xs text-amber-400">⚠ Could not reach backend — showing cached data.</p>
        )}
      </header>

      <div className="glass-card overflow-hidden rounded-2xl">
        <div className="grid grid-cols-[110px_1fr_140px_120px_100px_80px] gap-4 border-b border-white/5 bg-white/[0.02] px-5 py-3 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
          <span>Tx Hash</span>
          <span>Flow</span>
          <span className="text-right">Amount</span>
          <span>Status</span>
          <span>Risk</span>
          <span className="text-right">Latency</span>
        </div>

        {isLoading && !data ? (
          <div className="space-y-px">
            {Array.from({ length: 7 }).map((_, i) => (
              <div key={i} className="animate-pulse h-14 bg-white/[0.015] px-5" />
            ))}
          </div>
        ) : (
          rows.map((t, i) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.35, delay: i * 0.04 }}
              className="grid grid-cols-[110px_1fr_140px_120px_100px_80px] items-center gap-4 border-b border-white/5 px-5 py-4 text-sm transition hover:bg-white/[0.03]"
            >
              <span className="truncate font-mono text-[11px] text-zinc-400">{t.id}</span>
              <span className="flex min-w-0 items-center gap-2 font-mono text-xs text-zinc-200">
                <span className="truncate">{t.from}</span>
                <ArrowRight className="size-3 shrink-0 text-zinc-600" />
                <span className="truncate text-zinc-400">{t.to}</span>
              </span>
              <span className="text-right font-display font-semibold text-white">
                {t.amount.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                <span className="ml-1 text-[10px] font-medium text-zinc-500">{t.currency}</span>
              </span>
              <span
                className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${statusStyle[t.status]}`}
              >
                {statusIcon[t.status]} {t.status}
              </span>
              <span className="flex items-center gap-2">
                <span className="h-1 w-14 overflow-hidden rounded-full bg-white/5">
                  <span
                    className="block h-full rounded-full"
                    style={{
                      width: `${t.riskScore * 100}%`,
                      background:
                        t.riskScore > 0.6
                          ? "linear-gradient(90deg,#f59e0b,#ef4444)"
                          : "linear-gradient(90deg,#3b82f6,#a855f7)",
                    }}
                  />
                </span>
                <span className="text-[10px] font-mono text-zinc-500">
                  {t.riskScore.toFixed(2)}
                </span>
              </span>
              <span className="text-right font-mono text-[11px] text-zinc-500">
                {t.latencyMs}ms
              </span>
            </motion.div>
          ))
        )}
      </div>
    </AppShell>
  );
}
