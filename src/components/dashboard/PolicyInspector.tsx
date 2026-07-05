import { AnimatePresence, motion } from "framer-motion";
import { X, FileCheck2, Check, Ban } from "lucide-react";
import type { Transaction } from "@/lib/mock-data";
import { useEffect } from "react";

interface Props {
  tx: Transaction | null;
  onClose: () => void;
}

function downloadReceipt(tx: Transaction) {
  const content = [
    "AETHER TAMPER-EVIDENT LEDGER RECEIPT",
    "=====================================",
    `Transaction ID : ${tx.id}`,
    `From           : ${tx.from}`,
    `To             : ${tx.to}`,
    `Amount         : $${tx.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })} ${tx.currency}`,
    `Purpose        : ${tx.purpose}`,
    `Status         : ${tx.status.toUpperCase()}`,
    `Risk Score     : ${tx.riskScore.toFixed(2)}`,
    `Latency        : ${tx.latencyMs}ms`,
    `Timestamp      : ${tx.timestamp}`,
    `Signer         : aether-core-eu-west-1`,
    "",
    "POLICY TRACE",
    "------------",
    ...tx.policyTrace.map((s) => `[${s.passed ? "PASS" : "FAIL"}] ${s.step}: ${s.detail}`),
  ].join("\n");

  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `aether-receipt-${tx.id}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

interface Props {
  tx: Transaction | null;
  onClose: () => void;
}

export function PolicyInspector({ tx, onClose }: Props) {
  useEffect(() => {
    if (!tx) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [tx, onClose]);

  return (
    <AnimatePresence>
      {tx && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-white/10 bg-[#0d0d10]/95 backdrop-blur-xl"
          >
            <div className="flex items-start justify-between border-b border-white/5 p-6">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
                  Policy Inspector
                </p>
                <p className="mt-1 font-mono text-xs text-zinc-400">{tx.id}</p>
              </div>
              <button
                onClick={onClose}
                className="grid size-8 place-items-center rounded-md border border-white/10 bg-white/[0.03] text-zinc-400 transition hover:text-white"
              >
                <X className="size-4" />
              </button>
            </div>

            <div className="flex-1 space-y-6 overflow-y-auto p-6">
              <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
                <div className="mb-1 text-[10px] font-medium uppercase tracking-widest text-zinc-500">
                  Amount
                </div>
                <div className="font-display text-3xl font-bold text-white">
                  $
                  {tx.amount.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}{" "}
                  <span className="text-xs font-medium text-zinc-500">{tx.currency}</span>
                </div>
                <div className="mt-1 flex flex-wrap gap-3 text-[11px] text-zinc-400">
                  <span>
                    <span className="text-zinc-500">from</span>{" "}
                    <span className="font-mono text-white">{tx.from}</span>
                  </span>
                  <span>
                    <span className="text-zinc-500">to</span>{" "}
                    <span className="font-mono text-white">{tx.to}</span>
                  </span>
                </div>
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-[11px] font-semibold uppercase tracking-widest text-zinc-500">
                    Risk score
                  </span>
                  <span
                    className={`font-mono text-xs font-bold ${
                      tx.riskScore > 0.6
                        ? "text-rose-400"
                        : tx.riskScore > 0.3
                          ? "text-amber-400"
                          : "text-emerald-400"
                    }`}
                  >
                    {tx.riskScore.toFixed(2)} ·{" "}
                    {tx.riskScore > 0.6 ? "High" : tx.riskScore > 0.3 ? "Watch" : "Low"}
                  </span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.max(4, tx.riskScore * 100)}%` }}
                    transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
                    className={
                      tx.riskScore > 0.6
                        ? "h-full bg-rose-500"
                        : tx.riskScore > 0.3
                          ? "h-full bg-amber-500"
                          : "h-full bg-emerald-500"
                    }
                  />
                </div>
              </div>

              <div>
                <h4 className="mb-4 text-[11px] font-semibold uppercase tracking-widest text-zinc-500">
                  Policy logic trace
                </h4>
                <div className="relative space-y-4">
                  <div className="absolute bottom-2 left-[10px] top-2 w-px bg-white/5" />
                  {tx.policyTrace.map((s, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -6 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.35, delay: 0.15 + i * 0.1 }}
                      className="relative flex gap-3"
                    >
                      <span
                        className={`relative z-10 mt-0.5 grid size-5 shrink-0 place-items-center rounded-full border ${
                          s.passed
                            ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-400"
                            : "border-rose-500/40 bg-rose-500/15 text-rose-400"
                        }`}
                      >
                        {s.passed ? <Check className="size-3" /> : <Ban className="size-3" />}
                      </span>
                      <div>
                        <p className="text-xs font-semibold text-white">{s.step}</p>
                        <p className="mt-0.5 text-[11px] text-zinc-500">{s.detail}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/40 p-4 font-mono text-[10px] leading-relaxed text-zinc-500">
                <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-widest text-zinc-400">
                  <FileCheck2 className="size-3" /> Ledger receipt
                </div>
                <div>hash: 9c4a2b…f2019d</div>
                <div>block: 18,209,442</div>
                <div>anchor: L2 · settled in {tx.latencyMs}ms</div>
                <div>signer: aether-core-eu-west-1</div>
              </div>
            </div>

            <div className="border-t border-white/5 p-4">
              <button
                onClick={() => downloadReceipt(tx)}
                className="w-full rounded-lg bg-white py-2.5 text-sm font-semibold text-black transition hover:bg-zinc-100"
              >
                Download tamper-evident receipt
              </button>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
