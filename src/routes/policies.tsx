import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, Zap, Globe, DollarSign, Lock, Users, Plus, X } from "lucide-react";
import { AppShell } from "@/components/dashboard/AppShell";
import { usePolicies, useUpdatePolicy, useCreatePolicy } from "@/hooks/useApi";
import type { LucideIcon } from "lucide-react";
import type { PolicyResponse, PolicyCreateRequest } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/policies")({
  head: () => ({
    meta: [
      { title: "Policies — Aether" },
      { name: "description", content: "Programmable policies governing agent-to-agent commerce." },
    ],
  }),
  component: PoliciesPage,
});

const fallbackPolicies = [
  { icon: DollarSign, name: "spend-ceiling-v3", scope: "All agents", triggers: 4128, blocks: 42, status: "active", detail: "Rolling 1h cap per agent-org pair. Hard block > 3σ deviation from baseline.", id: "", agent_id: null, daily_limit: 100000, allowed_categories: "gpu_compute,inference,storage", max_transaction_amount: 10000, approval_threshold: 40, velocity_limit_per_minute: 60, version: 1 },
  { icon: Globe, name: "eu-cross-border", scope: "EU jurisdiction", triggers: 892, blocks: 12, status: "active", detail: "Escalates cross-border settlements > €10k to human on-call for GDPR/PSD3 review.", id: "", agent_id: null, daily_limit: 50000, allowed_categories: "all", max_transaction_amount: 10000, approval_threshold: 60, velocity_limit_per_minute: 20, version: 1 },
  { icon: Lock, name: "identity-strict", scope: "All agents", triggers: 19842, blocks: 1204, status: "active", detail: "Requires mTLS + verifiable credential signed by W3C registry issuer.", id: "", agent_id: null, daily_limit: 500000, allowed_categories: "all", max_transaction_amount: 50000, approval_threshold: 20, velocity_limit_per_minute: 120, version: 1 },
  { icon: Zap, name: "velocity-guard", scope: "New agents (< 30d)", triggers: 620, blocks: 88, status: "active", detail: "Rate-limits new agents to 40 tx / minute until reputation ≥ 90.", id: "", agent_id: null, daily_limit: 5000, allowed_categories: "gpu_compute,inference", max_transaction_amount: 500, approval_threshold: 40, velocity_limit_per_minute: 40, version: 1 },
  { icon: Users, name: "org-allowlist", scope: "Enterprise tier", triggers: 210, blocks: 0, status: "monitor", detail: "Restricts counterparties to explicit allowlist per workspace policy.", id: "", agent_id: null, daily_limit: 1000000, allowed_categories: "all", max_transaction_amount: 100000, approval_threshold: 30, velocity_limit_per_minute: 200, version: 1 },
  { icon: ShieldCheck, name: "anomaly-v2.4", scope: "All agents", triggers: 30240, blocks: 302, status: "active", detail: "ML anomaly detector on payload entropy + graph topology. Retrains nightly.", id: "", agent_id: null, daily_limit: 500000, allowed_categories: "all", max_transaction_amount: 50000, approval_threshold: 50, velocity_limit_per_minute: 100, version: 1 },
];

function iconForPolicy(name: string): LucideIcon {
  const n = name.toLowerCase();
  if (n.includes("spend") || n.includes("limit")) return DollarSign;
  if (n.includes("eu") || n.includes("border") || n.includes("global")) return Globe;
  if (n.includes("identity") || n.includes("auth")) return Lock;
  if (n.includes("velocity") || n.includes("rate")) return Zap;
  if (n.includes("allow") || n.includes("org")) return Users;
  return ShieldCheck;
}

type EditablePolicy = PolicyResponse & { icon?: LucideIcon };

function EditPolicyModal({ policy, onClose }: { policy: EditablePolicy; onClose: () => void }) {
  const update = useUpdatePolicy();
  const [form, setForm] = useState({
    name: policy.name,
    scope: policy.scope,
    daily_limit: policy.daily_limit,
    max_transaction_amount: policy.max_transaction_amount,
    approval_threshold: policy.approval_threshold,
    velocity_limit_per_minute: policy.velocity_limit_per_minute,
    allowed_categories: policy.allowed_categories,
    status: policy.status,
    detail: policy.detail,
  });

  const handleSave = async () => {
    if (!policy.id) return toast.error("Cannot edit static policy — backend not connected");
    try {
      await update.mutateAsync({ id: policy.id, body: form });
      toast.success("Policy updated");
      onClose();
    } catch {
      toast.error("Failed to update policy");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="glass-card w-full max-w-lg rounded-2xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="font-display text-lg font-bold text-white">Edit Policy</h2>
          <button onClick={onClose} className="grid size-8 place-items-center rounded-md border border-white/10 text-zinc-400 hover:text-white">
            <X className="size-4" />
          </button>
        </div>
        <div className="space-y-4">
          {[
            { label: "Name", key: "name" as const, type: "text" },
            { label: "Scope", key: "scope" as const, type: "text" },
            { label: "Daily Limit ($)", key: "daily_limit" as const, type: "number" },
            { label: "Max Transaction ($)", key: "max_transaction_amount" as const, type: "number" },
            { label: "Approval Threshold (%)", key: "approval_threshold" as const, type: "number" },
            { label: "Velocity Limit (tx/min)", key: "velocity_limit_per_minute" as const, type: "number" },
            { label: "Allowed Categories", key: "allowed_categories" as const, type: "text" },
          ].map(({ label, key, type }) => (
            <label key={key} className="block">
              <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">{label}</div>
              <input
                type={type}
                value={form[key]}
                onChange={(e) => setForm((f) => ({ ...f, [key]: type === "number" ? parseFloat(e.target.value) || 0 : e.target.value }))}
                className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white outline-none focus:border-accent-primary/50"
              />
            </label>
          ))}
          <label className="block">
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Status</div>
            <select
              value={form.status}
              onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
              className="w-full rounded-lg border border-white/10 bg-[#0d0d10] px-3 py-2 text-sm text-white outline-none focus:border-accent-primary/50"
            >
              <option value="active">Active</option>
              <option value="monitor">Monitor</option>
              <option value="disabled">Disabled</option>
            </select>
          </label>
          <label className="block">
            <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Description</div>
            <textarea
              value={form.detail}
              onChange={(e) => setForm((f) => ({ ...f, detail: e.target.value }))}
              rows={3}
              className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white outline-none focus:border-accent-primary/50 resize-none"
            />
          </label>
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={onClose} className="rounded-lg border border-white/10 px-4 py-2 text-sm text-zinc-400 hover:text-white">Cancel</button>
          <button onClick={handleSave} disabled={update.isPending} className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black hover:bg-zinc-100 disabled:opacity-60">
            {update.isPending ? "Saving…" : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  );
}

function CreatePolicyModal({ onClose }: { onClose: () => void }) {
  const create = useCreatePolicy();
  const [form, setForm] = useState<PolicyCreateRequest>({
    agent_id: "",
    name: "",
    daily_limit: 10000,
    allowed_categories: "gpu_compute,inference,storage",
    max_transaction_amount: 5000,
    approval_threshold: 40,
  });

  const handleCreate = async () => {
    if (!form.name?.trim()) return toast.error("Policy name is required");
    try {
      await create.mutateAsync(form);
      toast.success("Policy created");
      onClose();
    } catch {
      toast.error("Failed to create policy");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="glass-card w-full max-w-md rounded-2xl p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="font-display text-lg font-bold text-white">Create Policy</h2>
          <button onClick={onClose} className="grid size-8 place-items-center rounded-md border border-white/10 text-zinc-400 hover:text-white">
            <X className="size-4" />
          </button>
        </div>
        <div className="space-y-4">
          {[
            { label: "Policy Name", key: "name" as const, type: "text", placeholder: "e.g. my-policy-v1" },
            { label: "Daily Limit ($)", key: "daily_limit" as const, type: "number", placeholder: "10000" },
            { label: "Max Transaction ($)", key: "max_transaction_amount" as const, type: "number", placeholder: "5000" },
            { label: "Approval Threshold (%)", key: "approval_threshold" as const, type: "number", placeholder: "40" },
            { label: "Allowed Categories", key: "allowed_categories" as const, type: "text", placeholder: "gpu_compute,inference" },
          ].map(({ label, key, type, placeholder }) => (
            <label key={key} className="block">
              <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">{label}</div>
              <input
                type={type}
                value={form[key] ?? ""}
                placeholder={placeholder}
                onChange={(e) => setForm((f) => ({ ...f, [key]: type === "number" ? parseFloat(e.target.value) || 0 : e.target.value }))}
                className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-accent-primary/50"
              />
            </label>
          ))}
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={onClose} className="rounded-lg border border-white/10 px-4 py-2 text-sm text-zinc-400 hover:text-white">Cancel</button>
          <button onClick={handleCreate} disabled={create.isPending} className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black hover:bg-zinc-100 disabled:opacity-60">
            {create.isPending ? "Creating…" : "Create Policy"}
          </button>
        </div>
      </div>
    </div>
  );
}

function PoliciesPage() {
  const { data, isLoading, isError } = usePolicies();
  const [editTarget, setEditTarget] = useState<EditablePolicy | null>(null);
  const [createOpen, setCreateOpen] = useState(false);

  const policies = data
    ? data.map((p) => ({ ...p, icon: iconForPolicy(p.name) }))
    : fallbackPolicies;

  return (
    <AppShell breadcrumb="Policies">
      <header className="flex flex-col gap-2">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-accent-primary">
          Policy engine
        </span>
        <div className="flex items-center justify-between">
          <h1 className="font-display text-4xl font-bold text-white">Active Policies</h1>
          <button
            onClick={() => setCreateOpen(true)}
            className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black hover:bg-zinc-100"
          >
            <Plus className="size-4" /> New Policy
          </button>
        </div>
        <p className="max-w-2xl text-sm text-zinc-400">
          Programmable rules evaluated against every transaction in under 4 ms. Compose identity,
          velocity, jurisdiction and ML-based checks into a single decision.
        </p>
        {isError && (
          <p className="text-xs text-amber-400">⚠ Could not reach backend — showing cached data.</p>
        )}
      </header>

      {isLoading && !data ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card animate-pulse rounded-2xl p-5 h-40" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {policies.map((p, i) => {
            const Icon = p.icon ?? ShieldCheck;
            return (
              <motion.div
                key={p.name}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
                className="glass-card glow-hover rounded-2xl p-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div className="grid size-10 place-items-center rounded-xl bg-accent-primary/10 text-accent-primary">
                      <Icon className="size-5" />
                    </div>
                    <div>
                      <div className="font-mono text-sm font-semibold text-white">{p.name}</div>
                      <div className="text-[11px] uppercase tracking-wider text-zinc-500">
                        {p.scope}
                      </div>
                    </div>
                  </div>
                  <span
                    className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${
                      p.status === "active"
                        ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                        : "border-amber-500/30 bg-amber-500/10 text-amber-300"
                    }`}
                  >
                    {p.status}
                  </span>
                </div>
                <p className="mt-4 text-xs leading-relaxed text-zinc-400">{p.detail}</p>
                <div className="mt-5 flex items-center gap-6 border-t border-white/5 pt-4">
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-zinc-500">
                      Evaluations
                    </div>
                    <div className="font-display text-lg font-bold text-white">
                      {p.triggers.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase tracking-wider text-zinc-500">Blocks</div>
                    <div className="font-display text-lg font-bold text-rose-300">
                      {p.blocks.toLocaleString()}
                    </div>
                  </div>
                  <button
                    onClick={() => setEditTarget(p as EditablePolicy)}
                    className="ml-auto rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-zinc-300 transition hover:bg-white/[0.06] hover:text-white"
                  >
                    Edit rule
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {editTarget && <EditPolicyModal policy={editTarget} onClose={() => setEditTarget(null)} />}
      {createOpen && <CreatePolicyModal onClose={() => setCreateOpen(false)} />}
    </AppShell>
  );
}
