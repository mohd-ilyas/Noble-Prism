import { Search, Bell, Plus, X } from "lucide-react";
import { useState } from "react";
import { AgentsApi, type AgentRegisterRequest } from "@/lib/api";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/hooks/useApi";

function DeployAgentModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState({ name: "", org: "", public_key: "", wallet_address: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!form.name.trim()) return setError("Agent name is required.");
    if (!form.public_key.trim()) return setError("Public key is required.");
    if (!form.wallet_address.trim()) return setError("Wallet address is required.");
    setLoading(true);
    try {
      await AgentsApi.register(form as AgentRegisterRequest);
      qc.invalidateQueries({ queryKey: queryKeys.agents });
      setSuccess(true);
      setTimeout(onClose, 1200);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Registration failed";
      setError(msg.includes("409") ? "Agent name or wallet address already registered." : msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="glass-card w-full max-w-md rounded-2xl p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="font-display text-lg font-bold text-white">Deploy Agent</h2>
          <button
            onClick={onClose}
            className="grid size-8 place-items-center rounded-md border border-white/10 text-zinc-400 hover:text-white"
          >
            <X className="size-4" />
          </button>
        </div>

        {success ? (
          <p className="text-center text-sm font-medium text-emerald-400">
            Agent registered successfully!
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { label: "Agent name", key: "name" as const, placeholder: "e.g. my-agent-01" },
              { label: "Organization", key: "org" as const, placeholder: "e.g. Acme Corp" },
              {
                label: "Public key",
                key: "public_key" as const,
                placeholder: "-----BEGIN PUBLIC KEY-----",
              },
              { label: "Wallet address", key: "wallet_address" as const, placeholder: "0x..." },
            ].map(({ label, key, placeholder }) => (
              <label key={key} className="block">
                <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
                  {label}
                </div>
                <input
                  value={form[key]}
                  onChange={set(key)}
                  placeholder={placeholder}
                  className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-accent-primary/50"
                />
              </label>
            ))}
            {error && <p className="text-xs text-rose-400">{error}</p>}
            <div className="flex justify-end gap-3 pt-1">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg border border-white/10 px-4 py-2 text-sm text-zinc-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black hover:bg-zinc-100 disabled:opacity-60"
              >
                {loading ? "Registering…" : "Register Agent"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export function TopHeader({ breadcrumb = "Aether Control Plane" }: { breadcrumb?: string }) {
  const [deployOpen, setDeployOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-white/5 bg-black/20 px-6 backdrop-blur-xl md:px-10">
        <div className="flex min-w-0 items-center gap-3 text-sm">
          <span className="text-zinc-500">Workspace</span>
          <span className="text-zinc-700">/</span>
          <span className="truncate font-semibold text-zinc-100">{breadcrumb}</span>
        </div>

        <div className="hidden flex-1 justify-center px-8 lg:flex">
          <div className="flex w-full max-w-md items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-zinc-500">
            <Search className="size-3.5" />
            <span>Search transactions, agents, policies…</span>
            <span className="ml-auto rounded border border-white/10 px-1.5 py-0.5 font-mono text-[10px]">
              ⌘K
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-medium text-zinc-400 sm:flex">
            <span className="relative flex size-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
            </span>
            Protocol Live
          </div>
          <button className="grid size-9 place-items-center rounded-lg border border-white/10 bg-white/[0.03] text-zinc-400 transition hover:text-white">
            <Bell className="size-4" />
          </button>
          <button
            onClick={() => setDeployOpen(true)}
            className="group relative inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black shadow-lg transition hover:bg-zinc-100"
          >
            <Plus className="size-4" />
            Deploy Agent
          </button>
        </div>
      </header>

      {deployOpen && <DeployAgentModal onClose={() => setDeployOpen(false)} />}
    </>
  );
}
