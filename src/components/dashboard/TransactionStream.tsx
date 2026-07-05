import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, CheckCircle2, Shield, AlertTriangle } from "lucide-react";
import type { Transaction, TxStatus } from "@/lib/mock-data";

const statusMeta: Record<TxStatus, { label: string; classes: string; Icon: typeof CheckCircle2 }> =
  {
    approved: {
      label: "Approved",
      classes: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
      Icon: CheckCircle2,
    },
    blocked: {
      label: "Blocked",
      classes: "border-rose-500/30 bg-rose-500/10 text-rose-400",
      Icon: Shield,
    },
    escalated: {
      label: "Escalated",
      classes: "border-amber-500/30 bg-amber-500/10 text-amber-400",
      Icon: AlertTriangle,
    },
  };

interface Props {
  transactions: Transaction[];
  onSelect: (tx: Transaction) => void;
  selectedId?: string;
}

export function TransactionStream({ transactions, onSelect, selectedId }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1], delay: 0.05 }}
      className="glass-card flex flex-col overflow-hidden rounded-3xl"
    >
      <div className="flex items-center justify-between border-b border-white/5 px-6 py-4">
        <div>
          <h3 className="font-display text-lg font-bold text-white">Agent Traffic Stream</h3>
          <p className="text-xs text-zinc-500">Live agent-to-agent payment authorizations</p>
        </div>
        <div className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1 text-[10px] font-medium text-zinc-400">
          <span className="relative flex size-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent-primary opacity-75" />
            <span className="relative inline-flex size-1.5 rounded-full bg-accent-primary" />
          </span>
          Streaming
        </div>
      </div>

      <div className="divide-y divide-white/5">
        <AnimatePresence initial={false}>
          {transactions.map((tx, i) => {
            const meta = statusMeta[tx.status];
            const active = tx.id === selectedId;
            return (
              <motion.button
                key={tx.id}
                layout
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
                onClick={() => onSelect(tx)}
                className={`group grid w-full grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)_auto_auto] items-center gap-4 px-6 py-4 text-left transition-colors ${
                  active ? "bg-accent-primary/[0.06]" : "hover:bg-white/[0.03]"
                }`}
              >
                <div className="flex min-w-0 items-center gap-3">
                  <div className="grid size-8 shrink-0 place-items-center rounded-lg border border-white/10 bg-white/[0.04] font-mono text-[10px] text-zinc-400">
                    TX
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 text-sm font-medium text-white">
                      <span className="truncate">{tx.from}</span>
                      <ArrowRight className="size-3 shrink-0 text-zinc-600" />
                      <span className="truncate text-zinc-300">{tx.to}</span>
                    </div>
                    <p className="mt-0.5 truncate text-[11px] text-zinc-500">
                      {tx.purpose || "—"} ·{" "}
                      {tx.timestamp?.includes("T")
                        ? new Date(tx.timestamp).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                            second: "2-digit",
                          })
                        : tx.timestamp}
                    </p>
                  </div>
                </div>

                <div>
                  <div className="font-mono text-sm font-semibold text-white">
                    $
                    {tx.amount.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </div>
                  <div className="text-[10px] uppercase tracking-wider text-zinc-500">
                    {tx.currency}
                  </div>
                </div>

                <span
                  className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${meta.classes}`}
                >
                  <meta.Icon className="size-3" />
                  {meta.label}
                </span>

                <span className="hidden font-mono text-[11px] text-zinc-500 md:inline">
                  {tx.id.slice(0, 6)}…{tx.id.slice(-3)}
                </span>
              </motion.button>
            );
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
