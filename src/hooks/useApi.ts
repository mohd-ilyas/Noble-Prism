/**
 * React Query hooks for all backend API calls.
 * Each hook falls back gracefully when the backend is unavailable.
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  AgentsApi,
  PoliciesApi,
  LedgerApi,
  InsightsApi,
  KillSwitchApi,
  TransactionsApi,
  CommerceApi,
  type TransactionRequest,
  type PolicyCreateRequest,
  type WorkflowCreateRequest,
} from "@/lib/api";

// ── Query keys ────────────────────────────────────────────────────────────────
export const queryKeys = {
  agents: ["agents"] as const,
  agent: (id: string) => ["agents", id] as const,
  policies: ["policies"] as const,
  ledger: (limit?: number) => ["ledger", limit ?? 50] as const,
  insights: ["insights"] as const,
  killswitch: ["killswitch"] as const,
  commerceProviders: ["commerce", "providers"] as const,
  workflows: ["commerce", "workflows"] as const,
};

// ── Agents ────────────────────────────────────────────────────────────────────
export function useAgents() {
  return useQuery({
    queryKey: queryKeys.agents,
    queryFn: () => AgentsApi.list(),
    staleTime: 15_000,
    retry: 1,
  });
}

export function useAgent(id: string) {
  return useQuery({
    queryKey: queryKeys.agent(id),
    queryFn: () => AgentsApi.get(id),
    enabled: Boolean(id),
    staleTime: 15_000,
    retry: 1,
  });
}

// ── Policies ─────────────────────────────────────────────────────────────────
export function usePolicies() {
  return useQuery({
    queryKey: queryKeys.policies,
    queryFn: () => PoliciesApi.list(),
    staleTime: 30_000,
    retry: 1,
  });
}

export function useCreatePolicy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: PolicyCreateRequest) => PoliciesApi.create(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.policies }),
  });
}

export function useUpdatePolicy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: Partial<PolicyCreateRequest> }) =>
      PoliciesApi.update(id, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.policies }),
  });
}

// ── Ledger ────────────────────────────────────────────────────────────────────
export function useLedger(limit = 50) {
  return useQuery({
    queryKey: queryKeys.ledger(limit),
    queryFn: () => LedgerApi.list(limit),
    staleTime: 10_000,
    retry: 1,
    refetchInterval: 15_000,
  });
}

// ── Insights ──────────────────────────────────────────────────────────────────
export function useInsights() {
  return useQuery({
    queryKey: queryKeys.insights,
    queryFn: () => InsightsApi.get(),
    staleTime: 20_000,
    retry: 1,
    refetchInterval: 30_000,
  });
}

// ── Kill Switch ───────────────────────────────────────────────────────────────
export function useActivateKillSwitch() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      agentId,
      reason,
      riskScore,
    }: {
      agentId: string;
      reason: string;
      riskScore?: number;
    }) => KillSwitchApi.activate(agentId, reason, riskScore),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.agents });
      qc.invalidateQueries({ queryKey: queryKeys.killswitch });
    },
  });
}

export function useReleaseKillSwitch() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ agentId, note }: { agentId: string; note?: string }) =>
      KillSwitchApi.release(agentId, note),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.agents });
      qc.invalidateQueries({ queryKey: queryKeys.killswitch });
    },
  });
}

// ── Transactions ──────────────────────────────────────────────────────────────
export function useInitiateTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: TransactionRequest) => TransactionsApi.initiate(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.ledger() });
      qc.invalidateQueries({ queryKey: queryKeys.insights });
      qc.invalidateQueries({ queryKey: queryKeys.agents });
    },
  });
}

export function useEvaluateTransaction() {
  return useMutation({
    mutationFn: (body: TransactionRequest) => TransactionsApi.evaluate(body),
  });
}

export function useApproveTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ transactionId, note }: { transactionId: string; note?: string }) =>
      TransactionsApi.approve(transactionId, note),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.ledger() });
      qc.invalidateQueries({ queryKey: queryKeys.insights });
    },
  });
}

export function useRejectTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ transactionId, reason }: { transactionId: string; reason?: string }) =>
      TransactionsApi.reject(transactionId, reason),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.ledger() });
      qc.invalidateQueries({ queryKey: queryKeys.insights });
    },
  });
}

export function useRegisterAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: import("@/lib/api").AgentRegisterRequest) => AgentsApi.register(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.agents });
      qc.invalidateQueries({ queryKey: queryKeys.insights });
    },
  });
}

export function useKillSwitchEvents() {
  return useQuery({
    queryKey: [...queryKeys.killswitch, "events"],
    queryFn: () => KillSwitchApi.events(),
    staleTime: 30_000,
    retry: 1,
  });
}

export function useNegotiationProviders() {
  return useQuery({
    queryKey: queryKeys.commerceProviders,
    queryFn: () => CommerceApi.providers(),
    staleTime: 15_000,
    retry: 1,
    refetchInterval: 20_000,
  });
}

export function useWorkflowStream() {
  return useQuery({
    queryKey: queryKeys.workflows,
    queryFn: () => CommerceApi.listWorkflows(),
    staleTime: 10_000,
    retry: 1,
    refetchInterval: 15_000,
  });
}

export function useCreateWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: WorkflowCreateRequest) => CommerceApi.createWorkflow(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.workflows });
      qc.invalidateQueries({ queryKey: queryKeys.insights });
    },
  });
}

export function useApproveWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ workflowId }: { workflowId: string }) => CommerceApi.approveWorkflow(workflowId),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.workflows }),
  });
}

export function useRetryWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ workflowId }: { workflowId: string }) => CommerceApi.retryWorkflow(workflowId),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.workflows }),
  });
}
