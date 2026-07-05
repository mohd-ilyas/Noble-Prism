import { createFileRoute } from "@tanstack/react-router";
import { useState, useMemo } from "react";
import { AppShell } from "@/components/dashboard/AppShell";
import { HeroSection } from "@/components/dashboard/HeroSection";
import { KpiStrip } from "@/components/dashboard/KpiStrip";
import { VolumeChart } from "@/components/dashboard/VolumeChart";
import { TransactionStream } from "@/components/dashboard/TransactionStream";
import { AgentRoster } from "@/components/dashboard/AgentRoster";
import { AiInsights } from "@/components/dashboard/AiInsights";
import { EventsTimeline } from "@/components/dashboard/EventsTimeline";
import { PolicyInspector } from "@/components/dashboard/PolicyInspector";
import { CommerceCommandCenter } from "@/components/dashboard/CommerceCommandCenter";
import { NegotiationDashboard } from "@/components/dashboard/NegotiationDashboard";
import { WorkflowTimeline } from "@/components/dashboard/WorkflowTimeline";
import { AgentGraph } from "@/components/dashboard/AgentGraph";
import { MarketplaceExplorer } from "@/components/dashboard/MarketplaceExplorer";
import { useLedger } from "@/hooks/useApi";
import { transactions as mockTransactions, type Transaction } from "@/lib/mock-data";
import type { LedgerEntry } from "@/lib/api";

export const Route = createFileRoute("/")({
  component: Index,
});

/** Map a live LedgerEntry to the Transaction shape expected by TransactionStream/PolicyInspector */
function ledgerToTransaction(e: LedgerEntry): Transaction {
  return {
    id: e.display_id ?? e.transaction_id,
    from: e.from,
    to: e.to,
    amount: e.amount,
    currency: e.currency as Transaction["currency"],
    purpose: e.purpose ?? "",
    status: (["approved", "blocked", "escalated"].includes(e.status)
      ? e.status
      : "escalated") as Transaction["status"],
    riskScore: e.riskScore ?? e.risk_score ?? 0,
    timestamp: e.timestamp,
    latencyMs: e.latencyMs ?? e.latency_ms ?? 0,
    policyTrace: e.policyTrace ?? [],
  };
}

function Index() {
  const { data: ledgerData } = useLedger(20);

  const transactions = useMemo<Transaction[]>(() => {
    if (ledgerData && ledgerData.length > 0) {
      return ledgerData.map(ledgerToTransaction);
    }
    return mockTransactions;
  }, [ledgerData]);

  const [selected, setSelected] = useState<Transaction | null>(null);

  return (
    <AppShell breadcrumb="Overview">
      <HeroSection />
      <KpiStrip />
      <CommerceCommandCenter />
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <VolumeChart />
        </div>
        <AiInsights />
      </div>
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <NegotiationDashboard />
        <WorkflowTimeline />
      </div>
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <TransactionStream
            transactions={transactions}
            onSelect={setSelected}
            selectedId={selected?.id}
          />
        </div>
        <div className="space-y-6">
          <AgentRoster />
          <EventsTimeline />
        </div>
      </div>
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <AgentGraph />
        <MarketplaceExplorer />
      </div>
      <PolicyInspector tx={selected} onClose={() => setSelected(null)} />
    </AppShell>
  );
}
