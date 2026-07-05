import { motion } from "framer-motion";
import { useWorkflowStream } from "@/hooks/useApi";

export function WorkflowTimeline() {
  const { data: workflows = [] } = useWorkflowStream();
  const workflow = workflows[0];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.15 }}
      className="glass-card rounded-3xl p-6"
    >
      <h3 className="font-display text-lg font-bold text-white">Workflow Timeline</h3>
      <p className="mt-1 text-xs text-zinc-500">Planner → negotiator → approval orchestrated through the automation layer.</p>
      <div className="mt-6 space-y-4">
        {workflow?.steps?.map((step, index) => (
          <div key={step.id} className="flex gap-3">
            <div className="flex flex-col items-center">
              <div className={`mt-1 size-2.5 rounded-full ${step.status === "completed" ? "bg-emerald-400" : "bg-zinc-600"}`} />
              {index < (workflow.steps?.length ?? 0) - 1 && <div className="mt-2 h-full w-px bg-white/10" />}
            </div>
            <div className="flex-1 rounded-2xl border border-white/10 bg-black/20 p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-semibold text-white">{step.step_name}</p>
                <span className="text-[10px] uppercase tracking-wider text-zinc-500">{step.status}</span>
              </div>
              <p className="mt-1 text-[11px] text-zinc-500">{step.detail}</p>
            </div>
          </div>
        )) ?? <div className="text-sm text-zinc-500">No workflow steps yet.</div>}
      </div>
    </motion.div>
  );
}
