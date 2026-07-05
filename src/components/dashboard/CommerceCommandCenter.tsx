import { motion } from "framer-motion";
import { Bot, Sparkles, ArrowRight, RefreshCw, CheckCircle2, AlertTriangle, Mic2 } from "lucide-react";
import { useApproveWorkflow, useCreateWorkflow, useRetryWorkflow, useWorkflowStream } from "@/hooks/useApi";
import { CommerceApi } from "@/lib/api";
import { toast } from "sonner";
import { useCommerceStore } from "@/store/commerceStore";
import { LiveStatusPill } from "./LiveStatusPill";

export function CommerceCommandCenter() {
  const { goalDraft, setGoalDraft } = useCommerceStore();
  const workflowMutation = useCreateWorkflow();
  const approveMutation = useApproveWorkflow();
  const retryMutation = useRetryWorkflow();
  const { data: workflows = [] } = useWorkflowStream();

  const handleCreate = async () => {
    if (!goalDraft.trim()) {
      toast.error("Describe a goal before launching a workflow");
      return;
    }
    try {
      const workflow = await workflowMutation.mutateAsync({ goal: goalDraft.trim(), amount: 125, currency: "USD" });
      toast.success(`Workflow launched: ${workflow.workflow_summary}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Workflow creation failed");
    }
  };

  const handleSimulate = async () => {
    if (!goalDraft.trim()) {
      toast.error("Describe a goal before simulating a decision");
      return;
    }
    try {
      const simulation = await CommerceApi.negotiate({ goal: goalDraft.trim(), amount: 125, currency: "USD" });
      toast.success(simulation.ai_summary ?? "Negotiation simulation completed");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Simulation failed");
    }
  };

  const handleApprove = async (workflowId: string) => {
    try {
      await approveMutation.mutateAsync({ workflowId });
      toast.success("Workflow approved and executed");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Approval failed");
    }
  };

  const handleRetry = async (workflowId: string) => {
    try {
      await retryMutation.mutateAsync({ workflowId });
      toast.success("Workflow retried");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Retry failed");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.05 }}
      className="glass-card rounded-3xl border border-white/10 p-6"
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.24em] text-accent-primary">
            <Bot className="size-3.5" /> 🤖 Jarvis automation
          </div>
          <h3 className="mt-2 font-display text-xl font-bold text-white">Autonomous Commerce OS</h3>
          <p className="mt-1 text-sm text-zinc-400">Convert goals into executable workflows, negotiate providers, and orchestrate approvals.</p>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <button
            type="button"
            title="Voice agent coming soon"
            aria-label="Voice agent coming soon"
            className="grid size-10 place-items-center rounded-full border border-sky-400/20 bg-sky-400/10 text-sky-300 shadow-[0_0_18px_rgba(56,189,248,0.12)] transition hover:border-sky-300/40 hover:text-white"
          >
            <Mic2 className="size-4" />
          </button>
          <div className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
            <LiveStatusPill />
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.4fr_0.8fr]">
        <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Goal</label>
          <textarea
            value={goalDraft}
            onChange={(e) => setGoalDraft(e.target.value)}
            className="mt-2 min-h-24 w-full rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3 text-sm text-white outline-none placeholder:text-zinc-600"
            placeholder="Describe the workflow you want to automate"
          />
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={handleCreate}
              disabled={workflowMutation.isPending}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-accent-primary to-accent-secondary px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-60"
            >
              {workflowMutation.isPending ? <RefreshCw className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
              ✨ Launch workflow
            </button>
            <button
              onClick={handleSimulate}
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2 text-sm text-zinc-300 transition hover:bg-white/[0.04]"
            >
              <ArrowRight className="size-4" /> Simulate decision
            </button>
          </div>
        </div>

        <div className="space-y-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">🛰 Recent automations</div>
          {workflows.slice(0, 3).map((workflow) => (
            <div key={workflow.id} className="rounded-xl border border-white/10 bg-black/20 p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium text-white">{workflow.goal}</p>
                {workflow.status === "running" ? (
                  <CheckCircle2 className="size-4 text-emerald-400" />
                ) : (
                  <AlertTriangle className="size-4 text-amber-400" />
                )}
              </div>
              <div className="mt-2 text-[11px] text-zinc-500">{workflow.workflow_summary}</div>
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => handleApprove(workflow.id)}
                  disabled={approveMutation.isPending || retryMutation.isPending}
                  className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-300 disabled:opacity-50"
                >
                  {approveMutation.isPending ? "Approving…" : "Approve"}
                </button>
                <button
                  onClick={() => handleRetry(workflow.id)}
                  disabled={approveMutation.isPending || retryMutation.isPending}
                  className="rounded-lg border border-amber-500/20 bg-amber-500/10 px-2.5 py-1 text-[11px] font-semibold text-amber-300 disabled:opacity-50"
                >
                  {retryMutation.isPending ? "Retrying…" : "Retry"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
