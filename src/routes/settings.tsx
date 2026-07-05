import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import { User, Bell, Key, Webhook, CreditCard, Shield } from "lucide-react";
import { AppShell } from "@/components/dashboard/AppShell";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings — Aether" },
      { name: "description", content: "Workspace, security, and integration settings for Aether." },
    ],
  }),
  component: SettingsPage,
});

const sections = [
  { id: "profile", label: "Workspace", icon: User },
  { id: "security", label: "Security", icon: Shield },
  { id: "api", label: "API Keys", icon: Key },
  { id: "webhooks", label: "Webhooks", icon: Webhook },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "billing", label: "Billing", icon: CreditCard },
] as const;

function SettingsPage() {
  const [active, setActive] = useState<(typeof sections)[number]["id"]>("profile");

  return (
    <AppShell breadcrumb="Settings">
      <header className="flex flex-col gap-2">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-accent-primary">
          Configuration
        </span>
        <h1 className="font-display text-4xl font-bold text-white">Settings</h1>
        <p className="max-w-2xl text-sm text-zinc-400">
          Manage your workspace, security posture, integrations and billing for the Aether control
          plane.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[240px_1fr]">
        <nav className="glass-card h-fit rounded-2xl p-2">
          {sections.map((s) => {
            const Icon = s.icon;
            const isActive = active === s.id;
            return (
              <button
                key={s.id}
                onClick={() => setActive(s.id)}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition ${
                  isActive
                    ? "bg-accent-primary/10 text-accent-primary"
                    : "text-zinc-400 hover:bg-white/[0.04] hover:text-white"
                }`}
              >
                <Icon className="size-4" />
                {s.label}
              </button>
            );
          })}
        </nav>

        <motion.div
          key={active}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="glass-card rounded-2xl p-6"
        >
          {active === "profile" && <ProfileSection />}
          {active === "security" && <SecuritySection />}
          {active === "api" && <ApiSection />}
          {active === "webhooks" && <WebhooksSection />}
          {active === "notifications" && <NotificationsSection />}
          {active === "billing" && <BillingSection />}
        </motion.div>
      </div>
    </AppShell>
  );
}

function Field({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <label className="block">
      <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
        {label}
      </div>
      <input
        defaultValue={value}
        className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white outline-none transition focus:border-accent-primary/50 focus:bg-white/[0.05]"
      />
      {hint && <div className="mt-1.5 text-[11px] text-zinc-500">{hint}</div>}
    </label>
  );
}

function Toggle({ label, hint, on = true }: { label: string; hint: string; on?: boolean }) {
  const [checked, setChecked] = useState(on);
  return (
    <div className="flex items-start justify-between gap-4 border-b border-white/5 py-4 last:border-0">
      <div>
        <div className="text-sm font-medium text-white">{label}</div>
        <div className="mt-1 text-xs text-zinc-500">{hint}</div>
      </div>
      <button
        onClick={() => setChecked(!checked)}
        className={`relative mt-1 h-6 w-11 shrink-0 rounded-full transition ${checked ? "bg-accent-primary" : "bg-white/10"}`}
      >
        <span
          className={`absolute top-0.5 size-5 rounded-full bg-white shadow transition ${checked ? "left-5" : "left-0.5"}`}
        />
      </button>
    </div>
  );
}

function Section({
  title,
  desc,
  children,
}: {
  title: string;
  desc: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h2 className="font-display text-xl font-bold text-white">{title}</h2>
      <p className="mt-1 text-sm text-zinc-400">{desc}</p>
      <div className="mt-6 space-y-4">{children}</div>
    </div>
  );
}

function ProfileSection() {
  return (
    <Section title="Workspace" desc="Basic identity for your control plane instance.">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Workspace name" value="Aether Control Plane" />
        <Field label="Slug" value="aether-prod" hint="Used in API endpoints" />
        <Field label="Region" value="us-east-1 · eu-west-3" />
        <Field label="Environment" value="production" />
      </div>
      <div className="flex justify-end pt-2">
        <button className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black transition hover:bg-zinc-100">
          Save changes
        </button>
      </div>
    </Section>
  );
}

function SecuritySection() {
  return (
    <Section title="Security" desc="Authentication and hardening controls.">
      <Toggle label="Require SSO for operators" hint="Enforce SAML for all human console access." />
      <Toggle
        label="Hardware key for policy edits"
        hint="Require WebAuthn confirmation before mutating live policies."
      />
      <Toggle
        label="IP allowlist for admin API"
        hint="Restrict admin token usage to declared CIDRs."
        on={false}
      />
      <Toggle
        label="Anomaly quarantine"
        hint="Auto-freeze agents flagged by anomaly-v2.4 pending review."
      />
    </Section>
  );
}

function ApiSection() {
  return (
    <Section title="API Keys" desc="Machine credentials for the Aether protocol API.">
      {[
        { name: "prod · signer", key: "ath_live_9f2c…4a11", created: "Mar 12, 2026" },
        { name: "prod · reader", key: "ath_live_c81d…f0aa", created: "Feb 04, 2026" },
        { name: "staging · signer", key: "ath_test_1a02…7c31", created: "Jan 22, 2026" },
      ].map((k) => (
        <div
          key={k.key}
          className="flex items-center justify-between rounded-xl border border-white/5 bg-white/[0.02] px-4 py-3"
        >
          <div>
            <div className="text-sm font-semibold text-white">{k.name}</div>
            <div className="mt-0.5 font-mono text-xs text-zinc-500">{k.key}</div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] text-zinc-500">Created {k.created}</span>
            <button className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-zinc-300 hover:bg-white/[0.05] hover:text-white">
              Rotate
            </button>
          </div>
        </div>
      ))}
      <button className="w-full rounded-xl border border-dashed border-white/15 py-3 text-sm font-medium text-zinc-400 transition hover:border-accent-primary/50 hover:text-white">
        + Generate new key
      </button>
    </Section>
  );
}

function WebhooksSection() {
  return (
    <Section title="Webhooks" desc="Receive protocol events at your endpoints.">
      <Field label="Settlement endpoint" value="https://hooks.acme.co/aether/settle" />
      <Field label="Policy trigger endpoint" value="https://hooks.acme.co/aether/policy" />
      <Field label="Anomaly endpoint" value="https://hooks.acme.co/aether/anomaly" />
      <Toggle
        label="Retry with exponential backoff"
        hint="Up to 6 attempts over 24h with jitter."
      />
    </Section>
  );
}

function NotificationsSection() {
  return (
    <Section title="Notifications" desc="Where the on-call team gets paged.">
      <Toggle label="Slack: #aether-alerts" hint="Blocked transactions and escalations." />
      <Toggle
        label="PagerDuty: SEV-1 incidents"
        hint="Anomaly cluster or ledger checkpoint failures."
      />
      <Toggle label="Email digest" hint="Daily summary at 08:00 local time." on={false} />
    </Section>
  );
}

function BillingSection() {
  return (
    <Section title="Billing" desc="Usage-based billing for protocol calls and settlement volume.">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
          <div className="text-[11px] uppercase tracking-wider text-zinc-500">Plan</div>
          <div className="mt-1 font-display text-2xl font-bold text-white">Enterprise</div>
        </div>
        <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
          <div className="text-[11px] uppercase tracking-wider text-zinc-500">MTD volume</div>
          <div className="mt-1 font-display text-2xl font-bold text-white">$4.28M</div>
        </div>
        <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4">
          <div className="text-[11px] uppercase tracking-wider text-zinc-500">
            Estimated invoice
          </div>
          <div className="mt-1 font-display text-2xl font-bold text-white">$12,420</div>
        </div>
      </div>
      <div className="flex justify-end">
        <button className="rounded-lg border border-white/10 px-4 py-2 text-sm font-medium text-zinc-300 hover:bg-white/[0.05] hover:text-white">
          Download invoices
        </button>
      </div>
    </Section>
  );
}
