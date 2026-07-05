import { DollarSign, ShieldOff, Timer, Users } from "lucide-react";
import { KpiCard } from "./KpiCard";
import { useInsights } from "@/hooks/useApi";

const spark1 = [22, 28, 24, 32, 30, 38, 34, 42, 40, 48, 52, 58];
const spark2 = [18, 14, 22, 16, 24, 12, 20, 14, 18, 10, 15, 8];
const spark3 = [22, 20, 18, 21, 19, 16, 18, 14, 15, 12, 14, 11];
const spark4 = [180, 195, 210, 224, 240, 258, 270, 288, 296, 302, 308, 312];

export function KpiStrip() {
  const { data } = useInsights();
  const kpis = data?.kpis;

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard
        label="Authorized Volume"
        value={kpis?.authorized_volume ?? 1_284_092}
        format={(n) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 0 })}`}
        delta="+12.4%"
        deltaTone="up"
        icon={DollarSign}
        spark={spark1}
        accent="primary"
        delay={0}
      />
      <KpiCard
        label="Blocked Requests"
        value={kpis?.blocked_requests ?? 1_402}
        format={(n) => `${Math.round(n).toLocaleString()}`}
        delta="-2.1%"
        deltaTone="down"
        icon={ShieldOff}
        spark={spark2}
        accent="danger"
        delay={0.08}
      />
      <KpiCard
        label="Avg Auth Latency"
        value={kpis?.avg_latency_ms ?? 14}
        format={(n) => `${Math.round(n)}ms`}
        delta="stable"
        deltaTone="flat"
        icon={Timer}
        spark={spark3}
        accent="secondary"
        delay={0.16}
      />
      <KpiCard
        label="Active Agents"
        value={kpis?.active_agents ?? 312}
        format={(n) => `${Math.round(n).toLocaleString()}`}
        delta="+18"
        deltaTone="up"
        icon={Users}
        spark={spark4}
        accent="success"
        delay={0.24}
      />
    </div>
  );
}
